import sys
sys.path.append('../../')
from stateful import Const, BloomFilter, MaybeContains


from generator_tools import *
from known_types import *  
from commands import *  
    
UID.reset()
fp = FlowProcessor(
        istruct=[('op', uint8_t), ('x',uint32_t)],
        ostruct=[('b',uint32_t), ('err', bool_t)],
        locals=[('comp_res',bool_t)],
        state=[ BloomFilter('mybloom',uint32_t, 1024), \
                            Const('op_add',uint8_t,ord('a')), \
                            Const('op_rem',uint8_t,ord('r')), \
                            Const('op_len',uint8_t,ord('l')) ]
    )

fp\
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
