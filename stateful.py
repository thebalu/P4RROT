
from known_types import KnownType
from typing import Dict, List, Tuple
from standard_fields import *
from generator_tools import *


class SharedVariable(SharedElement):
    
    def __init__(self,vname:str,vtype:KnownType):
        self.vaname = vname
        self.vtype = vtype

    def get_name(self):
        return self.vaname

    def get_type(self):
        return (SharedVariable,self.vtype)

    def get_generated_code(self):
        gc = GeneratedCode()
        gc.get_decl().writeln('#pragma netro reglocked register')
        gc.get_decl().writeln('register< {} >(1) {};'.format(self.vtype.get_p4_type(),self.vaname))
        return gc

    def get_repr(self):
        return [ None ]


class ReadFromShared(Command):
    
    def __init__(self,target:str,source:str,env=None):
        self.target = target
        self.source = source
        self.env = env
        if env!=None:
            self.check()

    def check(self):
        assert self.env.has_var(self.source), 'Undefined name: {}'.format(self.source)
        assert self.env.has_var(self.target), 'Undefined name: {}'.format(self.target)
        assert self.env.get_varinfo(self.source)['type'][0] == SharedVariable, 'This method should be applied on SharedVariables only'
        assert self.env.get_varinfo(self.source)['type'][1] == self.env.get_varinfo(self.target)['type'], 'Type mismatch'

    def get_generated_code(self):
        gc = GeneratedCode()
        s = self.env.get_varinfo(self.source)
        t = self.env.get_varinfo(self.target)
        gc.get_apply().writeln('{}.read({},0);'.format(s['handle'],t['handle']))
        return gc

    def execute(self,test_env):
        test_env[self.target] = test_env[self.source][0]



class WriteToShared(Command):
    
    def __init__(self,target:str,source:str,env=None):
        self.target = target
        self.source = source
        self.env = env
        if env!=None:
            self.check()

    def check(self):
        assert self.env.has_var(self.source), 'Undefined name: {}'.format(self.source)
        assert self.env.has_var(self.target), 'Undefined name: {}'.format(self.target)
        assert self.env.get_varinfo(self.target)['type'][0] == SharedVariable, 'This method should be applied on SharedVariables only'
        assert self.env.get_varinfo(self.target)['type'][1] == self.env.get_varinfo(self.source)['type'], 'Type mismatch'

    def get_generated_code(self):
        gc = GeneratedCode()
        s = self.env.get_varinfo(self.source)
        t = self.env.get_varinfo(self.target)
        gc.get_apply().writeln('{}.write(0,{});'.format(t['handle'],s['handle']))
        return gc

    def execute(self,test_env):
        test_env[self.target][0] = test_env[self.source]



class SharedArray(SharedElement):

    def __init__(self,vname:str,vtype:KnownType,size:int):
        self.vaname = vname
        self.vtype = vtype
        self.size = size

    def get_name(self):
        return self.vaname

    def get_type(self):
        return (SharedArray,self.vtype,self.size)

    def get_generated_code(self):
        gc = GeneratedCode()
        gc.get_decl().writeln('#pragma netro reglocked register')
        gc.get_decl().writeln('register< {} >({}) {};'.format(self.vtype.get_p4_type(),self.size,self.vaname))
        return gc

    def get_repr(self):
        return [None]*self.size



class ReadFromSharedAt(Command):
    
    def __init__(self,target:str,source:str,idx_vname:str,env=None):
        self.target = target
        self.source = source
        self.idx_vname = idx_vname
        self.env = env
        if env!=None:
            self.check()

    def check(self):
        assert self.env.has_var(self.source), 'Undefined name: {}'.format(self.source)
        assert self.env.has_var(self.target), 'Undefined name: {}'.format(self.target)
        assert self.env.has_var(self.idx_vname), 'Undefined name: {}'.format(self.idx_vname)
        assert self.env.get_varinfo(self.idx_vname)['type'] == uint32_t , 'Index should be uint32_t'
        assert self.env.get_varinfo(self.source)['type'][0] == SharedArray, 'This method should be applied on SharedVariables only'
        assert self.env.get_varinfo(self.source)['type'][1] == self.env.get_varinfo(self.target)['type'], 'Type mismatch'

    def get_generated_code(self):
        gc = GeneratedCode()
        s = self.env.get_varinfo(self.source)
        t = self.env.get_varinfo(self.target)
        idx = self.env.get_varinfo(self.idx_vname)
        gc.get_apply().writeln('{}.read({},{});'.format(s['handle'],t['handle'],idx['handle']))
        return gc

    def execute(self,test_env):
        s = self.env.get_varinfo(self.source)
        if test_env[self.idx_vname]>=s['type'][2]:
            raise Exception('{}[{}] : Value {} is out of range 0..{}'.format(self.source),test_env[self.idx_vname],test_env[self.idx_vname],s['type'][2]-1)
        test_env[self.target] = test_env[self.source][test_env[self.idx_vname]]



class WriteToSharedAt(Command):
    
    def __init__(self,target:str,idx_vname:str,source:str,env=None):
        self.target = target
        self.source = source
        self.idx_vname = idx_vname
        self.env = env
        if env!=None:
            self.check()

    def check(self):
        assert self.env.has_var(self.source), 'Undefined name: {}'.format(self.source)
        assert self.env.has_var(self.target), 'Undefined name: {}'.format(self.target)
        assert self.env.has_var(self.idx_vname), 'Undefined name: {}'.format(self.idx_vname)
        assert self.env.get_varinfo(self.idx_vname)['type'] == uint32_t , 'Index should be uint32_t'
        assert self.env.get_varinfo(self.target)['type'][0] == SharedArray, 'This method should be applied on SharedVariables only'
        assert self.env.get_varinfo(self.target)['type'][1] == self.env.get_varinfo(self.source)['type'], 'Type mismatch'

    def get_generated_code(self):
        gc = GeneratedCode()
        s = self.env.get_varinfo(self.source)
        t = self.env.get_varinfo(self.target)
        idx = self.env.get_varinfo(self.idx_vname)
        gc.get_apply().writeln('{}.write({},{});'.format(t['handle'],idx['handle'],s['handle']))
        return gc

    def execute(self,test_env):
        t = self.env.get_varinfo(self.target)
        if test_env[self.idx_vname]>=t['type'][2]:
            raise Exception('{}[{}] : Value {} is out of range 0..{}'.format(self.target),test_env[self.idx_vname],test_env[self.idx_vname],t['type'][2]-1)
        test_env[self.target][test_env[self.idx_vname]] = test_env[self.source]


class SharedStack(SharedElement):

    def __init__(self,vname:str,vtype:KnownType,capacity:int):
        self.vaname = vname
        self.index_name = self.vaname + '_idx'
        self.temp_name = self.vaname + "_temp"
        self.vtype = vtype
        self.capacity = capacity
        self.current_size = 0

    def get_name(self):
        return self.vaname

    def get_type(self):
        return (SharedStack,self.vtype,self.capacity)

    def get_generated_code(self):
        gc = GeneratedCode()
        gc.get_decl().writeln('#pragma netro reglocked register')
        gc.get_decl().writeln('register< {} >({}) {};'.format(self.vtype.get_p4_type(),self.capacity,self.vaname))
        gc.get_decl().writeln('register< {} >(1) {};'.format(uint32_t.get_p4_type(), self.index_name))
        gc.get_decl().writeln('{} {};'.format(uint32_t.get_p4_type(), self.temp_name))
        return gc

    def get_repr(self):
        return [None]*self.capacity



class PopFromStack(Command):
    
    def __init__(self,stack:str,value:str,env=None):
        self.stack = stack
        self.value = value
        self.index_name = self.stack + '_idx'
        self.temp_name = self.stack + '_temp'
        self.env = env
        if env!=None:
            self.check()

    def check(self):
        # assert self.env.has_var(self.source), 'Undefined name: {}'.format(self.source)
        # assert self.env.has_var(self.target), 'Undefined name: {}'.format(self.target)
        # assert self.env.has_var(self.index_name), 'Undefined name: {}'.format(self.index_name)
        # assert self.env.get_varinfo(self.idx_vname)['type'] == uint32_t , 'Index should be uint32_t'
        # assert self.env.get_varinfo(self.source)['type'][0] == SharedStack, 'This method should be applied on SharedStacks only'
        # assert self.env.get_varinfo(self.source)['type'][1] == self.env.get_varinfo(self.target)['type'], 'Type mismatch'
        True
        
    def get_generated_code(self):
        gc = GeneratedCode()
        v = self.env.get_varinfo(self.value)
        s = self.env.get_varinfo(self.stack)
        gc.get_apply().writeln('{}.read({},0);'.format(self.index_name, self.temp_name))
        gc.get_apply().writeln('{} = {} - 1;'.format(self.temp_name, self.temp_name))
        gc.get_apply().writeln('{}.read({},{});'.format(s['handle'],v['handle'], self.temp_name))
        gc.get_apply().writeln('{}.write(0,{});'.format(self.index_name,self.temp_name))
        return gc

    def execute(self,test_env):
        s = self.env.get_varinfo(self.value)
        # if test_env[self.idx_vname]>=s['type'][2]:
        #     raise Exception('{}[{}] : Value {} is out of range 0..{}'.format(self.source),test_env[self.idx_vname],test_env[self.idx_vname],s['type'][2]-1)
        # test_env[self.target] = test_env[self.source][test_env[self.idx_vname]]



class PushToStack(Command):
    
    def __init__(self,stack:str,value:str,env=None):
        self.stack = stack
        self.value = value
        self.index_name = self.stack + '_idx'
        self.temp_name = self.stack + '_temp'
        self.env = env
        if env!=None:
            self.check()

    def check(self):
       True

    def get_generated_code(self):
        gc = GeneratedCode()
        s = self.env.get_varinfo(self.stack)
        v = self.env.get_varinfo(self.value)
        gc.get_apply().writeln('{}.read({},0);'.format(self.index_name, self.temp_name))
        gc.get_apply().writeln('{}.write({},{});'.format(s['handle'],self.temp_name, v['handle']))
        gc.get_apply().writeln('{} = {} + 1;'.format(self.temp_name, self.temp_name))
        gc.get_apply().writeln('{}.write(0,{});'.format(self.index_name,self.temp_name))
        return gc

    def execute(self,test_env):
        return
        # t = self.env.get_varinfo(self.target)
        # if test_env[self.idx_vname]>=t['type'][2]:
        #     raise Exception('{}[{}] : Value {} is out of range 0..{}'.format(self.target),test_env[self.idx_vname],test_env[self.idx_vname],t['type'][2]-1)
        # test_env[self.target][test_env[self.idx_vname]] = test_env[self.source]


class BloomFilter(SharedElement):

    def __init__(self,vname:str,vtype:KnownType,capacity:int, number_of_hashes: int):
        self.vaname = vname
        self.reg_name = vname + '_register'
        self.index_name = self.reg_name + '_idx'
        self.temp_name = self.reg_name + "_temp"
        self.vtype = vtype
        self.capacity = capacity
        
        self.value_check = self.vaname + '_value_check'
        self.hash_name = self.vaname + '_hash'
        self.salt_name = self.vaname + '_salt'
        self.hashres_name = self.vaname + '_result'
        self.properties = {'capacity': capacity, 'number_of_hashes': number_of_hashes}

    def get_properties(self):
        return self.properties

    def get_name(self):
        return self.vaname

    def get_type(self):
        return (SharedStack,self.vtype,self.capacity)

    def get_generated_code(self):
        gc = GeneratedCode()
        gc.get_decl().writeln('#pragma netro reglocked register')
        gc.get_decl().writeln('register< bit<1> >({}) {};'.format(self.capacity, self.reg_name))
        # gc.get_decl().writeln('register< {} >(1) {};'.format(uint32_t.get_p4_type(), self.index_name))
        gc.get_decl().writeln('{} {};'.format(uint32_t.get_p4_type(), self.value_check))
        gc.get_decl().writeln('{} {};'.format(uint32_t.get_p4_type(), self.index_name))
        gc.get_decl().writeln('{} {};'.format(uint32_t.get_p4_type(), self.temp_name))
        gc.get_decl().writeln('{} {};'.format(uint32_t.get_p4_type(), self.hash_name))
        gc.get_decl().writeln('bit<1> {};'.format(self.hashres_name))
        return gc

    def get_repr(self):
        return [None]*self.capacity

class MaybeContains(Command):
    
    def __init__(self,result: str, bloom_filter:str,value:str,env=None):
        self.bloom_filter = bloom_filter
        self.value = value
        self.value_check = self.bloom_filter + '_value_check'
        self.reg_name = self.bloom_filter + '_register'
        self.index_name = self.bloom_filter + '_idx'
        self.temp_name = self.bloom_filter + '_temp'
        self.hash_name = self.bloom_filter + '_hash'
        self.salt_name = self.bloom_filter + '_salt'
        self.hashres_name = self.bloom_filter + '_result'
        self.env = env
        self.result = result
        if env!=None:
            self.check()

    def check(self):
        True
        
    def get_generated_code(self):
        gc = GeneratedCode()
        properties = (self.env.get_varinfo(self.bloom_filter))['properties']
        val_to_check = self.env.get_varinfo(self.value)

        # start with True
        gc.get_apply().writeln('{} = {};'.format(self.result, '(bit<8>)1'))         

        # this will be a parameter, how many hashes we want to calculate, now let's use fixed 4
        for i in range(properties['number_of_hashes']):
            gc.get_apply().writeln('hash({}, HashAlgorithm.crc16, (bit<32>) 0, '.format(self.hash_name) + '{' + \
                '{}, (bit<8>) {}'.format(val_to_check['handle'], str(i)) + '}, (bit<32>)' +  '{});'.format(str(properties['capacity'])))
        # concatenate instead of adding!
        # uid.get()
        # Kivulrol, felhasznalo altal parameterben adott dolgoknal kell a get_varinfo
        # code writer can indent stuff
            gc.get_apply().writeln('{}.read({}, {});'.format(self.reg_name, self.hashres_name, self.hash_name))
            gc.get_apply().writeln('if ({} != 1)'.format(self.hashres_name) + '{')
            gc.get_apply().increase_indent()
            gc.get_apply().writeln( '{} = (bit<8>) 0;'.format(self.result))
            gc.get_apply().decrease_indent()
            gc.get_apply().writeln('};')

        return gc

    def execute(self,test_env):
        s = self.env.get_varinfo(self.value)

class PutIntoBloom(Command):
    
    def __init__(self, bloom_filter:str,value:str,env=None):
        self.bloom_filter = bloom_filter
        self.value = value
        self.reg_name = self.bloom_filter + '_register'
        self.hash_name = self.bloom_filter + '_hash'
        self.env = env
        if env!=None:
            self.check()

    def check(self):
        True
        
    def get_generated_code(self):
        gc = GeneratedCode()
        properties = (self.env.get_varinfo(self.bloom_filter))['properties']
        val_to_check = self.env.get_varinfo(self.value)
        bloom_filter_var = self.env.get_varinfo(self.bloom_filter)        

        # this will be a parameter, how many hashes we want to calculate, now let's use fixed 4
        for i in range(properties['number_of_hashes']):
            gc.get_apply().writeln('hash({}, HashAlgorithm.crc16, (bit<32>) 0, '.format(self.hash_name) + '{' + \
                '{}, (bit<8>) {}'.format(val_to_check['handle'], str(i)) + '}, (bit<32>)' + '{});'.format(properties['capacity']))
            gc.get_apply().writeln('{}.write({}, (bit<1>) 1);'.format(self.reg_name, self.hash_name))

        return gc

    def execute(self,test_env):
        s = self.env.get_varinfo(self.value)



class Const(SharedElement):
    def __init__(self,vname:str,vtype:KnownType,value):
        self.vaname = vname
        self.vtype = vtype
        self.value = value

    def get_name(self):
        return self.vaname

    def get_type(self):
        return self.vtype

    def get_generated_code(self):
        gc = GeneratedCode()
        gc.get_headers().writeln('const {} {} = {};'.format(self.vtype.get_p4_type(),
                                                         self.vaname, 
                                                         self.vtype.to_p4_literal(self.value)))
        return gc

    def get_repr(self):
        return self.vtype.cast_value(self.value)
