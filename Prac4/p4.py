import threading
import time
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

#Global rate to be sampled by the thread method
rate = 10
#Global channels to be sampled by the thread method
chan = None
chan1 = None

def main():
    global chan, chan1, rate

    btn_num = 25

    #HARDWARE============================================================
    # create the spi bus
    spi = busio.SPI(clock=board.SCLK, MISO=board.MISO, MOSI=board.MOSI)

    # create the cs (chip select)
    cs = digitalio.DigitalInOut(board.D5)
    
    #create button instance as an digital input
    btn = digitalio.DigitalInOut(board.D25)
    btn.direction = digitalio.Direction.INPUT
    btn.pull = digitalio.Pull.UP
    
    #Create the mcp object
    mcp = MCP.MCP3008(spi, cs)

    # create an analog input channel on pin 2 - Light sensor
    chan = AnalogIn(mcp, MCP.P2)

    # create an analog input channe on pin 1 - Temperature sensor
    chan1 = AnalogIn(mcp, MCP.P1)

    #THREADING===========================================================    
    #Start thread with dedicated method, no args
    thread = threading.Thread(target=print_thread)
    thread.daemon = True
    thread.start()

    #BUTTON==============================================================
    while True:
        if btn.value == False:
            #Debouncing timer
            time.sleep(0.2)
            #Wait until button released          
            while(btn.value == False):
                pass
            #Change rate based on previous rate
            if rate == 10: rate = 5
            elif rate == 5: rate = 1
            else: rate = 10
    #====================================================================

def print_thread():
    #Thread method to sample values and print data repetitively
    print('{0:<15} {1:<15} {2:<15} {3:<15}'.format('Runtime:', 'Temp Reading', 'Temp', 'Light Reading'))
    runtime = 0
    while(True):
        start = time.time()
        print('{0:<15} {1:<15} {2:<15.2f} {3:<15}'.format(str(runtime)+'s', \
        chan1.value, round(chan1.voltage*100), chan.value))
        #Wait for specified sample rate      
        time.sleep(rate)
        #Calculate how much time has passed
        runtime = runtime + round(time.time() - start)

if __name__ == "__main__":
    main()
