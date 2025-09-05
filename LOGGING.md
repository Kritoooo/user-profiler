# 系统日志功能说明

用户画像系统现已支持完整的日志记录和监控功能，帮助你实时了解系统运行状态和调试问题。

## 🚀 快速开始

### 启动带日志的系统
```bash
# 启动系统并显示实时日志
./start_with_logs.sh
```

这会：
- 启动后端和前端服务
- 创建日志文件 `backend/logs/user_profiler.log`
- 在单独窗口显示实时日志（如果支持GUI）
- 提供多种日志查看方式

## 📋 日志查看方式

### 1. 命令行工具
```bash
# 查看最近30条日志
./view_logs.sh

# 实时跟踪日志（类似tail -f）
./view_logs.sh follow

# 查看最近100条日志
./view_logs.sh recent 100

# 只看错误日志
./view_logs.sh error

# 查看特定用户的日志
./view_logs.sh user testuser

# 查看API请求日志
./view_logs.sh api

# 查看所有可用选项
./view_logs.sh help
```

### 2. Web界面日志查看器
访问前端界面的日志页面：
- URL: http://localhost:3000/logs
- 功能：
  - 实时日志流
  - 按级别筛选（DEBUG, INFO, WARNING, ERROR）
  - 按用户ID筛选
  - 关键词搜索
  - 自动刷新开关
  - 导出日志文件

### 3. API端点
```bash
# 获取最近100条日志
curl http://localhost:8000/logs/recent?lines=100

# 实时日志流（Server-Sent Events）
curl http://localhost:8000/logs/stream
```

## 📊 日志内容说明

### 日志级别
- **DEBUG**: 详细的调试信息
- **INFO**: 一般信息，如操作开始/完成
- **WARNING**: 警告信息，系统仍可正常运行
- **ERROR**: 错误信息，操作失败但系统继续运行
- **CRITICAL**: 严重错误，可能导致系统中断

### 结构化日志格式
```
2024-01-01 10:30:45 | INFO     | [user:testuser] [github] Starting data collection
2024-01-01 10:30:47 | WARNING  | [user:testuser] LLM extraction failed for https://github.com/testuser: API key not configured
2024-01-01 10:30:48 | INFO     | [user:testuser] Collected 5 items from github (duration: 2.34s)
```

### 上下文信息
日志会自动包含相关的上下文信息：
- **user_id**: 当前处理的用户ID
- **platform**: 数据来源平台（github, zhihu等）
- **operation**: 当前执行的操作
- **url**: 相关的URL地址
- **duration**: 操作耗时

## 🔧 配置选项

### 环境变量（backend/.env）
```bash
# 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
LOG_LEVEL=INFO

# 日志文件路径
LOG_FILE=logs/user_profiler.log

# 是否使用JSON格式（便于程序解析）
LOG_JSON_FORMAT=false
```

### 日志文件位置
- **默认位置**: `backend/logs/user_profiler.log`
- **自动创建**: logs目录会自动创建
- **文件轮转**: 当前版本不支持，可手动删除重新开始

## 🐛 调试技巧

### 追踪特定用户的处理过程
```bash
# 开始爬取
curl -X POST http://localhost:8000/crawl \
  -H "Content-Type: application/json" \
  -d '{"user_id": "testuser", "platforms": ["github"]}'

# 在另一个终端实时查看该用户的日志
./view_logs.sh user testuser | grep -v "^$"

# 或者使用实时跟踪
./view_logs.sh follow | grep "testuser"
```

### 监控错误情况
```bash
# 持续监控错误日志
./view_logs.sh follow | grep -E "(ERROR|CRITICAL|❌)"

# 查看最近的错误
./view_logs.sh error
```

### 性能监控
日志包含操作耗时信息，可以用来分析性能：
```bash
# 查看耗时信息
./view_logs.sh | grep "duration"

# 查看特定平台的性能
./view_logs.sh | grep "github.*duration"
```

## 📈 日志统计

### Web界面统计
访问 http://localhost:3000/logs 可以看到：
- 总日志数量
- 错误数量
- 警告数量
- 最后更新时间

### 命令行统计
```bash
# 统计各级别日志数量
grep -c "INFO" backend/logs/user_profiler.log
grep -c "ERROR" backend/logs/user_profiler.log
grep -c "WARNING" backend/logs/user_profiler.log

# 统计用户活动
grep -o "\[user:[^]]*\]" backend/logs/user_profiler.log | sort | uniq -c
```

## 🔄 日志轮转和清理

### 手动清理
```bash
# 清空日志文件
> backend/logs/user_profiler.log

# 或者删除后重新启动（会自动创建）
rm backend/logs/user_profiler.log
```

### 归档建议
对于生产环境，建议定期归档日志：
```bash
# 按日期归档
mv backend/logs/user_profiler.log backend/logs/user_profiler.log.$(date +%Y%m%d)

# 压缩旧日志
gzip backend/logs/user_profiler.log.*

# 删除7天前的日志
find backend/logs/ -name "*.log.*.gz" -mtime +7 -delete
```

## ❓ 常见问题

### Q: 看不到日志输出？
A: 检查以下几点：
1. 确保使用了 `./start_with_logs.sh` 启动
2. 检查 `backend/logs/` 目录是否存在
3. 确认后端服务正常启动
4. 查看 LOG_LEVEL 设置是否过高

### Q: 日志文件太大怎么办？
A: 
1. 临时提高LOG_LEVEL到WARNING或ERROR
2. 手动清理或归档旧日志
3. 重启服务

### Q: 无法在GUI中显示日志终端？
A: 
- 在WSL或无GUI环境中，日志会在主终端显示
- 可以使用 `./view_logs.sh follow` 在单独终端查看
- 或使用Web界面 http://localhost:3000/logs

### Q: 如何调试特定功能？
A:
1. 临时设置 LOG_LEVEL=DEBUG
2. 重启系统
3. 执行相关操作
4. 查看详细的DEBUG日志

这个完整的日志系统让你能够：
- 实时监控系统状态
- 快速定位和调试问题  
- 分析系统性能表现
- 追踪用户处理流程