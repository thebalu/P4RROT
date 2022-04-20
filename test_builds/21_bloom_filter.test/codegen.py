import sys
sys.path.append('../../')
from stateful import Const, BloomFilter, MaybeContains, PutIntoBloom


from generator_tools import *
from known_types import *  
from commands import *  
    
UID.reset()
fp = FlowProcessor(
        istruct=[('op', uint8_t), ('x',uint32_t)],
        ostruct=[('b',uint32_t), ('err', bool_t)],
        locals=[('comp_res',bool_t)],
        state=[ BloomFilter('mybloom',uint32_t, 123, 3) ]
    )

fp\
.add(PutIntoBloom('mybloom', 'x')) \
.add(Comment('this is a comment')) \
.add(MaybeContains('comp_res', 'mybloom', 'x')) \
.add(SendBack())
fs = FlowSelector(
        'IPV4_UDP',
        [(UdpDstPort,5555)],
        fp
    )

solution = Solution()
solution.add_flow_processor(fp)
solution.add_flow_selector(fs)
solution.get_generated_code().dump('test.p4app')
