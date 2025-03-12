import os
from nacos_middleware import NacosServiceMiddleware

def load_config_from_env():
    """从环境变量加载配置"""
    return {
        "nacos": {
            "server_addresses": os.getenv('NACOS_SERVER', 'http://localhost:8848'),
            "namespace": os.getenv('NACOS_NAMESPACE', 'public'),
            "username": os.getenv('NACOS_USERNAME', 'nacos'),
            "password": os.getenv('NACOS_PASSWORD', 'nacos')
        }
    }

def main():
    # 从环境变量加载配置
    config = load_config_from_env()
    
    # 初始化中间件
    middleware = NacosServiceMiddleware(config['nacos'])
    
    # 从环境变量获取服务端口，默认为5000
    port = int(os.getenv('PORT', '5000'))
    
    # 启动服务
    middleware.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    main()
