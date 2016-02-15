'''Various utilities of the chemview package

'''
import base64
import numpy as np

def encode_numpy(array):
    '''Encode a numpy array as a base64 encoded string, to be JSON serialized. 

    :return: a dictionary containing the fields:
                - *data*: the base64 string
                - *type*: the array type
                - *shape*: the array shape

    '''
    return {'data' : base64.b64encode(array.data).decode('utf8'),
            'type' : array.dtype.name,
            'shape': array.shape}

def beta_sheet_normals(ca, c, o):

    c_to_ca = normalized(ca - c)
    c_to_o = normalized(c - o)
    
    normals = np.cross(c_to_ca, c_to_o)
    # Make sure that angles are less than 90 degrees
    for i, n in enumerate(normals[1:]):
        if normals[i].dot(normals[i-1]) < 0:
            normals[i] *= -1
    
    return normals

def alpha_helix_normals(ca):
    K_AVG = 5
    K_OFFSET = 2
    
    if len(ca) <= K_AVG:
        start = ca[0]
        end = ca[-1]
        helix_dir = normalized(end - start)
        
        position = ca - start
        projected_pos = np.array([np.dot(r, helix_dir) * helix_dir for r in position]) 
        normals = normalized(position - projected_pos)
        return [start] * len(normals), [end] * len(normals), normals
    
    # Start and end point for normals
    starts = []
    ends = []
    

    for i in range(len(ca) - K_AVG):
        starts.append(ca[i:i + K_AVG - K_OFFSET].mean(axis=0))
        ends.append(ca[i+K_OFFSET:i + K_AVG].mean(axis=0))
        
    starts = np.array(starts)
    ends = np.array(ends)
    
    # position relative to "start point"
    normals = []
    for i,r in enumerate(ca):
        k = i if i < len(ca) - K_AVG else -1
        position = r - starts[k]
        # Find direction of the helix
        helix_dir = normalized(ends[k] - starts[k])
        # Project positions on the helix
        
        projected_pos = np.dot(position, helix_dir) * helix_dir        
        normals.append(normalized(position - projected_pos))


    return np.array(normals)

def normalized(vec):
    return vec / np.linalg.norm(vec)

def get_atom_color(atom_name):

    atomColors = {
        "H": 0xFFFFFF,
        "HE": 0xD9FFFF,
        "LI": 0xCC80FF,
        "BE": 0xC2FF00,
        "B": 0xFFB5B5,
        "C": 0x909090,
        "N": 0x3050F8,
        "O": 0xFF0D0D,
        "F": 0x90E050,
        "NE": 0xB3E3F5,
        "NA": 0xAB5CF2,
        "MG": 0x8AFF00,
        "AL": 0xBFA6A6,
        "SI": 0xF0C8A0,
        "P": 0xFF8000,
        "S": 0xFFFF30,
        "CL": 0x1FF01F,
        "AR": 0x80D1E3,
        "K": 0x8F40D4,
        "CA": 0x3DFF00,
        "SC": 0xE6E6E6,
        "TI": 0xBFC2C7,
        "V": 0xA6A6AB,
        "CR": 0x8A99C7,
        "MN": 0x9C7AC7,
        "FE": 0xE06633,
        "CO": 0xF090A0,
        "NI": 0x50D050,
        "CU": 0xC88033,
        "ZN": 0x7D80B0,
        "GA": 0xC28F8F,
        "GE": 0x668F8F,
        "AS": 0xBD80E3,
        "SE": 0xFFA100,
        "BR": 0xA62929,
        "KR": 0x5CB8D1,
        "RB": 0x702EB0,
        "SR": 0x00FF00,
        "Y": 0x94FFFF,
        "ZR": 0x94E0E0,
        "NB": 0x73C2C9,
        "MO": 0x54B5B5,
        "TC": 0x3B9E9E,
        "RU": 0x248F8F,
        "RH": 0x0A7D8C,
        "PD": 0x006985,
        "AG": 0xC0C0C0,
        "CD": 0xFFD98F,
        "IN": 0xA67573,
        "SN": 0x668080,
        "SB": 0x9E63B5,
        "TE": 0xD47A00,
        "I": 0x940094,
        "XE": 0x429EB0,
        "CS": 0x57178F,
        "BA": 0x00C900,
        "LA": 0x70D4FF,
        "CE": 0xFFFFC7,
        "PR": 0xD9FFC7,
        "ND": 0xC7FFC7,
        "PM": 0xA3FFC7,
        "SM": 0x8FFFC7,
        "EU": 0x61FFC7,
        "GD": 0x45FFC7,
        "TB": 0x30FFC7,
        "DY": 0x1FFFC7,
        "HO": 0x00FF9C,
        "ER": 0x00E675,
        "TM": 0x00D452,
        "YB": 0x00BF38,
        "LU": 0x00AB24,
        "HF": 0x4DC2FF,
        "TA": 0x4DA6FF,
        "W": 0x2194D6,
        "RE": 0x267DAB,
        "OS": 0x266696,
        "IR": 0x175487,
        "PT": 0xD0D0E0,
        "AU": 0xFFD123,
        "HG": 0xB8B8D0,
        "TL": 0xA6544D,
        "PB": 0x575961,
        "BI": 0x9E4FB5,
        "PO": 0xAB5C00,
        "AT": 0x754F45,
        "RN": 0x428296,
        "FR": 0x420066,
        "RA": 0x007D00,
        "AC": 0x70ABFA,
        "TH": 0x00BAFF,
        "PA": 0x00A1FF,
        "U": 0x008FFF,
        "NP": 0x0080FF,
        "PU": 0x006BFF,
        "AM": 0x545CF2,
        "CM": 0x785CE3,
        "BK": 0x8A4FE3,
        "CF": 0xA136D4,
        "ES": 0xB31FD4,
        "FM": 0xB31FBA,
    }

    return atomColors.get(atom_name.upper(), 0xFFFFFF)
