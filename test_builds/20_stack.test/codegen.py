import sys
sys.path.append('../../')
from stateful import PopFromStack, PushToStack, SharedStack


from generator_tools import *
from known_types import *  
from commands import *  
    
UID.reset()
fp = FlowProcessor(
        istruct=[('a',uint32_t),('b',uint32_t)],
        state=[ SharedStack('shared_stack',uint32_t, 10) ]
    )

fp\
.add(PushToStack('shared_stack', 'a'))\
.add(PopFromStack('shared_stack', 'b'))\
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
