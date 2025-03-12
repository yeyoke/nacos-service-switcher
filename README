nacos-service-switcher is a lightweight HTTP middleware that provides simple RESTful APIs to control the online/offline status of Nacos service instances. It allows you to manage service availability without modifying the original service implementation or restarting the service. Perfect for maintenance windows, blue-green deployments, and service traffic control.
Key Features:
- Simple RESTful APIs for service status control
- Environment variable based configuration
- Preserves original service metadata
- Supports multiple namespaces and groups
- Detailed operation logging
- No service code modification required

nacos-service-switcher 是一个轻量级的 HTTP 中间件，通过 RESTful API 提供 Nacos 服务实例的上下线控制功能。它允许您在不修改原始服务实现或重启服务的情况下管理服务可用性。特别适用于维护窗口、蓝绿部署和服务流量控制场景。
主要特性：
- 简单的 RESTful API 用于服务状态控制
- 基于环境变量的配置方式
- 保留原有服务元数据
- 支持多命名空间和分组
- 详细的操作日志记录
- 无需修改服务代码

nacos-service-switcher is a lightweight HTTP middleware that provides simple RESTful APIs to control the online/offline status of Nacos service instances. It allows you to manage service availability without modifying the original service implementation or restarting the service.

🚀 Perfect for:
- Maintenance windows and system upgrades
- Blue-green deployments
- Service traffic control
- A/B testing
- Emergency service isolation

✨ Key Features:
- Simple RESTful APIs for service status control
- Environment variable based configuration
- Preserves original service metadata
- Supports multiple namespaces and groups
- Detailed operation logging
- No service code modification required

💡 Common Use Cases:
1. System Maintenance
   ```bash
   # Take service offline before maintenance
   curl "http://localhost:5000/service/my-service/192.168.1.100/8080/down"
   # Bring service back online after maintenance
   curl "http://localhost:5000/service/my-service/192.168.1.100/8080/up"
   ```

2. Rolling Updates
   ```bash
   # Gradually update services in a cluster
   curl "http://localhost:5000/service/my-service/192.168.1.101/8080/down"
   # Deploy new version
   curl "http://localhost:5000/service/my-service/192.168.1.101/8080/up"
   # Repeat for each instance
   ```

3. Traffic Control
   ```bash
   # Temporarily redirect traffic by taking specific instances offline
   curl "http://localhost:5000/service/my-service/192.168.1.102/8080/down?group=BLUE_GROUP"
   ```

🔧 Quick Start:
