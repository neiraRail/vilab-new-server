import struct

def parseBytes(bytes):
    ''' Parse the binary data into a dictionary of the data '''
    # TODO: Add error handling
    raw_data = struct.unpack('ffffffffffiiii', bytes)
    data = {}
    data['ax'] = raw_data[0]
    data['ay'] = raw_data[1]
    data['az'] = raw_data[2]
    data['gx'] = raw_data[3]
    data['gy'] = raw_data[4]
    data['gz'] = raw_data[5]
    data['mx'] = raw_data[6]
    data['my'] = raw_data[7]
    data['mz'] = raw_data[8]
    data['tp'] = raw_data[9]
    data['st'] = raw_data[10]
    data['nd'] = raw_data[11]
    data['tm'] = raw_data[12]
    data['dt'] = raw_data[13]
    return data