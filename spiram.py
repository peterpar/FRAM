# library for SPI SRAM
 
from machine import SPI,Pin
import re

class SpiRam(object) :

    WREN = 0x6 # Set Write Enable Latch 0000 0110B
    WRDI = 0x4 # Reset Write Enable Latch 0000 0100B
    RDSR = 0x5 # Read Status Register 0000 0101B
    WRSR = 0x1 # Write Status Register 0000 0001B
    READ = 0x3 # Read Memory Code 0000 0011B
    WRITE = 0x2 # Write Memory Code 0000 0010B
    RDID = 0x9f # Read Device ID 1001 1111B
    FSTRD = 0xb # Fast Read Memory Code 0000 1011B
    SLEEP = 0xb9 #  Sleep Mode 1011 1001B




    def rdid(self) :
        self.cs(0)
        self.id = self.spi.read(5, self.RDID )
        self.cs(1)    

        density = (self.id[3] & 0x1f)
        self.size = 32768 * density
             

    def get_idstring(self):
        str = ""
        for i in range(1,5,1):
           if i > 1 :
               str+= ":"
           str += hex(self.id[ i ])
       
        return str
  
 
    def __init__( self, spiobj, csPin, debug=False ) :
    
        self.cs = machine.Pin(csPin, machine.Pin.OUT, machine.Pin.PULL_UP)
        self.spi = spiobj
        self.rdid()
        self.debug = debug
        
         
    @micropython.native    
    def get_address3B( self, address ) :
        cmds = bytearray(3)
        cmds[2] = address & 0xff
        address = address >> 8
        cmds[1] = address & 0xff
        address = address >> 8
        cmds[0] = address & 0xff
        return cmds
   
    def debug_ba( self, ba ) :
        print("".join("\\x%02x" % i for i in ba))
         
 
    def set_wren( self, wren ):
        self.cs(0)
        cmd = bytearray(1)
        if( wren ) :
            cmd[0] = self.WREN
        else:
            cmd[0] = self.WRDI
            
        self.spi.write( cmd )
        self.cs(1)
        
    # search entire memory for pattern of bytes
    def search_nonzero( self  ):
        
        self.cs(0)
        cmds = bytearray(5)
        cmds[0] = self.FSTRD
        cmds[1:4] = self.get_address3B(0)
        cmds[4] = 0xff # dummy
        
        block_size = 1024
        buf = bytearray(block_size)
        self.spi.write( cmds )
        for ix in range(0,self.size,block_size):
            self.spi.readinto( buf )
            for iy in range(0,block_size):
                if( buf[iy] != 0x0 ) :
                    print("Found at:" + hex( ix + iy ) )
             
        residual = self.size % block_size
          
        if( residual > 0 ) :
            lastbuf = bytearray(residual) 
            self.spi.read_into( lastbuf )
            matched = re.search(b'.*^\x00.*', buf).group(0)
            if( matched != Nul ) :
                print("Found nonzero after address:" + hex(ix) + " bytes were:" + hex(matched) )
        self.cs(1)
        
     
        
 
    def poke( self, address, ba ):
        cmds = bytearray(4)
        cmds[0] = self.WRITE
        cmds[1:4] = self.get_address3B(address)
        
        self.cs(0)
        if self.debug:
            self.debug_ba( cmds )
       
        self.spi.write( cmds )
        self.spi.write( ba )
        self.cs(1)
        
        
   
    # return byte at address
    def peek( self, address, nbytes ) :
        cmds = bytearray(4)
        cmds[0] = self.READ
        cmds[1:4] = self.get_address3B(address)
         
        if( self.debug ):
            self.debug_ba( cmds )
        self.cs(0)
        self.spi.write( cmds )
        
        res = bytearray(nbytes)
        # outputs dummy and reads back data
        self.spi.write_readinto( res, res )

        self.cs(1)
        
        return res
         
         
    def test_rdwr( self ):
        str = self.get_idstring()
        print(str)

        print("read it")
        res = self.peek( 100, 10 )

        self.debug_ba( res )


        self.set_wren( True )

        print("poke it")
        self.poke( 100, b'1234567890' )

        self.set_wren( False )


        res = self.peek( 100, 10 )

        print("read it again")
        self.debug_ba( res )
                  
 
spi = SPI(0 , baudrate=52000000, polarity=0, phase=0, bits = 8, sck=Pin(2), mosi=Pin(3),miso=Pin(4) )
    
    
ram = SpiRam(spi,5)
print("start search")
ram.search_nonzero()
print("done")


