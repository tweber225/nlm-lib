from dirigo.sw_interfaces.display import ColorVector




class Hematoxylin(ColorVector):
    """
    Hematoxylin color vector.
    
    RGB triplet values from QuPath default.
    """
    slug = "hematoxylin"
    label = "Hematoxylin"
    rgb = (0.65111, 0.70119, 0.29049)


class Eosin(ColorVector):
    """
    Eosin color vector.
    
    RGB triplet values from QuPath default.
    """
    slug = "eosin"
    label = "Eosin"
    rgb = (0.2159, 0.8012, 0.5581)


class DAB(ColorVector):
    """
    DAB (3,3'-diaminobenzidine) color vector. Warning: light extinction with DAB
    behaves very non-linearly, meaning the standard chromogenic-mimicking color
    algorithm will not be very realistic. 
    
    RGB triplet values from QuPath default.
    """
    slug = "dab"
    label = "DAB"
    rgb = (0.26917, 0.56824, 0.77759)