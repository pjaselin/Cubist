from random import randint

class cubist:
    def __init__(self, x, y, 
                 committees = 1, 
                 control = cubistControl(), 
                 weights=None, 
                 **kwargs):
        pass


def cubistControl(unbiased: bool = False, 
                  rules: int = 100, 
                  extrapolation: int = 100, 
                  sample: float = 0.0, 
                  seed = randint(0, 4095), 
                  label: str = "outcome"):
    if rules is not None and (rules < 1 or rules > 1000000):
        raise ValueError("number of rules must be between 1 and 1000000")
    if extrapolation < 0 or extrapolation > 100:
        raise ValueError("percent extrapolation must be between 0 and 100")
    if sample < 0.0 or sample > 99.9:
        raise ValueError("sampling percentage must be between 0.0 and 99")
    return dict(
        unbiased=unbiased,
        rules=rules,
        extrapolation=extrapolation/100,
        sample=sample/100,
        label = label,
        seed = seed%4095 #TODO: this isn't right
    )
