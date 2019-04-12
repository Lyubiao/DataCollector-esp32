# Data-collector
该项目是基于esp32的micropython开发，目的是要做电力的监控。它可以采集基本的电压，电流，功率，温度，湿度，开关量等数据，同时可以通过网络远程控制继电器来控制排插的开关。我负责的大部分的硬件选型设计和硬件程序的开发，micropython的底层支持，数据加密，数据库，服务器，网页则由[Juwan](https://github.com/junhuanchen)大佬负责。由于考虑到实际的情况和一些特殊的要求，采用的是ESP32+M5310A方案，也就是同时存在WIFI和NBIOT，
