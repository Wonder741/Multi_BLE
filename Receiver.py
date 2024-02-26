import asyncio
from bleak import BleakClient, BleakScanner, BleakError
from datetime import datetime
import os

UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E" 
UART_TXD_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RXD_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"

# Get the current system time and format it to a suitable string for a filename获取系统时间作为文件名
current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
directory = "C:\\Users\\cgwan\\Desktop\\Folders\\Ble_file"
#"D:\\UQ Learning\\7382\\realTimeTransmission\\receiver\\testData" # 数据储存地址（绝对地址）Data storage address (absolute address)
filename = f"{directory}\\{current_time}.txt"
#filename = f"{current_time}.txt"
if not os.path.exists(directory):
        os.makedirs(directory)
with open(f"{directory}\\{current_time}.txt", 'w') as file:
 file.write("Begin")
 file.write('\n')

#-------------------生成文件Generate txt file and write message from device--------------------------------------------------------------
async def save_message_to_file(message):
    with open(filename, 'a') as file:
        file.write(message)
        #file.write('\n')
    #print(f"Message saved to {filename}") 

#-------------------扫描并选择蓝牙设备Scan and select Bluetooth devices--------------------------------------------------------------
async def discover_devices():
    devices = await BleakScanner.discover()#启动 BLE 设备扫描 Initiate BLE device scanning
    devices_with_names = [(device, device.rssi) for device in devices if device.name]#未命名的设备将被过滤掉 Unnamed devices will be filtered out
    for index, (device, rssi) in enumerate(devices_with_names):# 枚举和打印设备列表 Enumerate and print a list of devices
        print(f"Index: {index}, Name: {device.name}, RSSI: {rssi}")
    return [device for device, _ in devices_with_names]

# ------------------Notification handler接收通知数据---------------------------------------------------------------------------------------
def notification_handler(sender: int, data: bytearray):
    message = data.decode('utf-8')
    #print(f"Received Message from {sender}: {message}")
    #if message.endswith('@'):
        #asyncio.create_task(save_message_to_file(message))
    asyncio.create_task(save_message_to_file(message))

# ------------------通知类型传输数据 Notification Type Transfer Data--------------------------------------------------------------------------------------- 
async def communicate_with_device(device):
    try:
        async with BleakClient(device.address) as client:
            # 启动特性通知 Start notifications on the characteristic
            await client.start_notify(UART_TXD_UUID, notification_handler)

            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S \n')
            print(f"Current date and time: {current_time}")
                # 发送当前时间 Send current time to device 
            await client.write_gatt_char(UART_RXD_UUID, current_time.encode())#使用该方法获取、打印当前日期和时间，然后发送到设备write_gatt_char 
                                                                              #Use this method to get and print the current date and time and send it to the device write_gatt_char
            await asyncio.sleep(5) 

            print("Started notifications. Waiting for data...")
            await asyncio.sleep(300)  # 保持连接 5 分钟（或根据需要进行调整）Keep the connection alive for 5 minutes (or adjust as needed)
            
            # 停止通知 Stop notifications
            await client.stop_notify(UART_TXD_UUID)
    except BleakError as e:
        print(f"Communication error: {e}")

'''
async def communicate_with_device(device):#非通知类型 Non-notification type Transfer Data
    try:
        async with BleakClient(device.address) as client: #使用其地址建立与 BLE 设备的连接。该async with语句确保当您完成与设备的通信时连接正确关闭
            

                           
            while True:
                message_parts = []
                # Get current date and time 获取当前时间
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S \n')
                print(f"Current date and time: {current_time}")
                # Send current time to device 发送当前时间
                await client.write_gatt_char(UART_RXD_UUID, current_time.encode())#使用该方法获取、打印当前日期和时间，然后发送到设备write_gatt_char
                await asyncio.sleep(5) 
                
                # Read data from device
                response = await client.read_gatt_char(UART_TXD_UUID)#从指定的 BLE 设备特性中读取数据(非通知类型)

                #print(f"Raw Response: {response}")#如果您没有看到任何输出，则意味着您没有接收到数据或者数据可能为空。
                
                if not response:
                    print("Received empty response.")
                    continue  # Skip the rest of the loop and wait for the next response

                message_parts.append(response.decode())#接收到的数据 ( response) 被解码（通常从字节到字符串），然后附加到列表中message_parts
                if message_parts[-1].endswith('@'):
                    full_message = ''.join(message_parts)
                    print("Received Message:", full_message)
                    #该代码检查最后收到的消息部分（即message_parts[-1]）是否以“@”字符结尾。如果是，则假定已收到完整消息。然后将存储的消息的所有部分message_parts连接起来形成完整的消息 ( full_message)，然后将其打印。
                    save_message_to_file(full_message) 
                

                await asyncio.sleep(5)
    except BleakError as e:
        print(f"Communication error: {e}") 
'''

async def main():
    devices_with_names = await discover_devices()#使用该函数发现具有名称的 BLE 设备discover_devices。Use this function to discover BLE devices with the name discover_devices.
    
    if not devices_with_names:
        print("No devices with names found. Exiting.")
        return

    try:
        choice = int(input("Enter the index of the device you want to connect to: "))#该行提示用户输入索引。它尝试将输入转换为整数。The line prompts the user for an index. It tries to convert the input to an integer
        if choice < 0 or choice >= len(devices_with_names):#这将检查输入的索引 ( choice) 是否在有效范围内。如果不是，它会打印一条错误消息并退出。
                                                           #This checks to see if the input index (choice) is in the valid range. If not, it prints an error message and exits.
            print("Invalid choice. Please choose a valid index.")
            return
        
        chosen_device = devices_with_names[choice]#用户提供有效索引后，代码从devices_with_names列表中获取相应的设备。After the user provides a valid index, the code fetches the appropriate device from the devices_with_names list.
        await communicate_with_device(chosen_device)#使用communicate_with_device异步函数启动与所选设备的通信。Use the communicate_with_device asynchronous function to initiate communication with the selected device.
    except ValueError:#如果用户输入的不是有效整数，ValueError则会引发 a。该块捕获该异常并通知用户 ValueError is raised if the user enters anything other than a valid integer. a. This block catches the exception and notifies the user of the
        print("Please enter a valid integer.")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
