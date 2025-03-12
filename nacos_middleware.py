from flask import Flask, request, jsonify
import nacos
import socket
import threading
import time
import logging
from typing import Dict, Optional
import json
import requests

class NacosServiceMiddleware:
    def __init__(self, nacos_config: Dict):
        """
        初始化 Nacos 服务中间件
        
        Args:
            nacos_config: Nacos配置信息
            {
                "server_addresses": "http://localhost:8848",
                "namespace": "public",
                "username": "nacos",
                "password": "nacos"
            }
        """
        self.client = nacos.NacosClient(
            server_addresses=nacos_config["server_addresses"],
            namespace=nacos_config.get("namespace", "public"),
            username=nacos_config.get("username"),
            password=nacos_config.get("password")
        )
        
        # 保存 Nacos 服务器地址
        self.nacos_server = nacos_config["server_addresses"].rstrip('/')
        self.registered_services = {}  # 存储已注册的服务
        self.heartbeat_threads = {}    # 存储心跳线程
        self.app = Flask(__name__)
        self.setup_routes()
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def setup_routes(self):
        """设置 API 路由"""
        
        @self.app.route('/service/<service_name>/<ip>/<int:port>/up', methods=['GET'])
        def service_up(service_name, ip, port):
            """上线服务"""
            try:
                group_name = request.args.get('group', 'DEFAULT_GROUP')
                metadata = {'enabled': 'true'}
                
                success = self.update_service_status(
                    service_name, ip, port, metadata, group_name
                )
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': f'Service {service_name} is up'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Failed to bring service up'
                    }), 500
                    
            except Exception as e:
                self.logger.error(f"Service up error: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': str(e)
                }), 500

        @self.app.route('/service/<service_name>/<ip>/<int:port>/down', methods=['GET'])
        def service_down(service_name, ip, port):
            """下线服务"""
            try:
                group_name = request.args.get('group', 'DEFAULT_GROUP')
                metadata = {'enabled': 'false'}
                
                success = self.update_service_status(
                    service_name, ip, port, metadata, group_name
                )
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': f'Service {service_name} is down'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Failed to bring service down'
                    }), 500
                    
            except Exception as e:
                self.logger.error(f"Service down error: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': str(e)
                }), 500

        @self.app.route('/service/<service_name>/<ip>/<int:port>/status', methods=['GET'])
        def service_status(service_name, ip, port):
            """获取服务状态"""
            try:
                group_name = request.args.get('group', 'DEFAULT_GROUP')
                service_key = f"{service_name}_{ip}_{port}"
                
                if service_key in self.registered_services:
                    service_info = self.registered_services[service_key]
                    is_enabled = service_info.get('metadata', {}).get('enabled', 'true')
                    return jsonify({
                        'success': True,
                        'status': 'up' if is_enabled == 'true' else 'down',
                        'service_info': service_info
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Service not found'
                    }), 404
                    
            except Exception as e:
                self.logger.error(f"Get service status error: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': str(e)
                }), 500

    def register_service_to_nacos(
        self, 
        service_name: str, 
        ip: str, 
        port: int, 
        metadata: Dict = None,
        group_name: str = 'DEFAULT_GROUP'
    ) -> bool:
        """
        向 Nacos 注册服务
        """
        try:
            metadata = metadata or {'enabled': 'true'}
            
            # 注册服务实例，添加 cluster_name 参数
            success = self.client.add_naming_instance(
                service_name=service_name,
                ip=ip,
                port=port,
                metadata=metadata,
                group_name=group_name,
                cluster_name='DEFAULT',  # 指定集群名称
                ephemeral=True
            )
            
            if success:
                service_key = f"{service_name}_{ip}_{port}"
                self.registered_services[service_key] = {
                    'service_name': service_name,
                    'ip': ip,
                    'port': port,
                    'metadata': metadata,
                    'group_name': group_name,
                    'cluster_name': 'DEFAULT'  # 保存集群信息
                }
                
                self._start_heartbeat(service_key)
                self.logger.info(f"Service registered: {service_key}, metadata: {metadata}")
                return True
            
            self.logger.error(f"Failed to register service: {service_name}")
            return False
            
        except Exception as e:
            self.logger.error(f"Register service error: {str(e)}")
            return False

    def update_service_status(
        self, 
        service_name: str, 
        ip: str, 
        port: int, 
        metadata: Dict,
        group_name: str = 'DEFAULT_GROUP'
    ) -> bool:
        """
        更新服务状态
        """
        try:
            service_key = f"{service_name}_{ip}_{port}"
            is_enabled = metadata.get('enabled', 'true') == 'true'
            
            # 构建 Nacos API URL
            api_url = f"{self.nacos_server}/nacos/v1/ns/instance"
            
            # 准备请求参数
            params = {
                'serviceName': service_name,
                'ip': ip,
                'port': port,
                'enabled': str(is_enabled).lower(),
                'groupName': group_name,
                'clusterName': 'DEFAULT',
                'ephemeral': 'true',
                'weight': '1.0',
                'namespaceId': self.client.namespace  # 添加命名空间参数
            }
            
            # 获取当前实例信息以保留元数据
            service_info = self.client.get_naming_instance(
                service_name=service_name,
                ip=ip,
                port=port
            )
            
            if service_info and 'metadata' in service_info:
                params['metadata'] = json.dumps(service_info['metadata'])
            
            self.logger.info(f"Sending request to Nacos: {api_url} with params: {params}")  # 添加调试日志
            
            # 发送 PUT 请求到 Nacos API
            response = requests.put(api_url, params=params)
            
            if response.status_code == 200 and response.text == 'ok':
                self.logger.info(f"Service status updated to {'enabled' if is_enabled else 'disabled'}: {service_key}")
                return True
            
            self.logger.error(f"Failed to update service status: {response.text}")
            self.logger.error(f"Response status code: {response.status_code}")  # 添加状态码日志
            return False
            
        except Exception as e:
            self.logger.error(f"Update service status error: {str(e)}")
            return False

    def _start_heartbeat(self, service_key: str):
        """启动服务心跳线程"""
        if service_key in self.heartbeat_threads:
            return

        def heartbeat_task():
            service_info = self.registered_services.get(service_key)
            if not service_info:
                return

            while service_key in self.heartbeat_threads:
                try:
                    self.client.send_heartbeat(
                        service_name=service_info['service_name'],
                        ip=service_info['ip'],
                        port=service_info['port'],
                        metadata=service_info.get('metadata', {})
                    )
                    time.sleep(5)  # 每5秒发送一次心跳
                except Exception as e:
                    self.logger.error(f"Heartbeat error for {service_key}: {str(e)}")
                    time.sleep(1)

        thread = threading.Thread(target=heartbeat_task, daemon=True)
        self.heartbeat_threads[service_key] = thread
        thread.start()

    def _stop_heartbeat(self, service_key: str):
        """停止服务心跳线程"""
        if service_key in self.heartbeat_threads:
            self.heartbeat_threads.pop(service_key, None)

    def run(self, host: str = '0.0.0.0', port: int = 5000):
        """启动中间件服务"""
        self.logger.info(f"Starting Nacos middleware on {host}:{port}")
        self.app.run(host=host, port=port) 