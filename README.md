# wechat_dat_to_image
Convert WeChat .dat to image  
将微信保存的加密图片 `.dat` 转换成图像格式 `.jpg`, `.png`, `.gif`  

## 加密方式:  
对每位字节进行**异或**计算  
异或 XOR: 二进制计算, 相同位得 0, 不同位得 1  
a XOR b = c, a XOR c = b  

图像格式前 2 位字节:  
- jpg: ff, d8  
- png: 89, 50  
- gif: 47, 49  

## 步骤：
1. 二进制读取 `.dat`
2. 判断 (`dat`第1个字节 XOR 图像格式[0]) 是否等于 (`dat`第2个字节 XOR 图像格式[1])  
3. 等于: 得到图像格式, 密码即为 `dat`第1个字节 XOR 图像格式[0]
4. 对 `dat` 每位字节 XOR 密码, 写入新图像文件  

## 使用:  
```
python main.py -h
# 单个 dat
python main.py -i 3d6296d68e01767a9476.dat
# 目录
python main.py -i "WeChat Files\wxid_\FileStorage\MsgAttach"
```
