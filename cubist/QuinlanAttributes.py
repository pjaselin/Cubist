
def quinlan_attributes(x):
    col_types = x.dtypes.to_dict()

    for col in col_types:
        if col_types[col] in ["float64", "int64"]:
            col_types[col] = "continuous."
        elif col_types[col] == "object":
            col_types[col] = f"{','.join(set(x[col]))}."
        elif col_types[col] == "bool":
            return

    return col_types
# class QuinlanAttributes:
#     def __init__(self, x):
#         self.x = x
#
#     def __str__(self):
#         return "string"
#
#     def __int__(self):
#         return "int"
#
#     def __float__(self):
#         return "float"

    # @staticmethod
    # def numeric(self):
    #     return "continuous ."
    #
    # @staticmethod
    # def string(self):
    #     return None
    #
    # @staticmethod
    # def date(self):
    #     return None
    #
    # @staticmethod
    # def dataframe(self):
    #     return None

print(QuinlanAttributes(5.0))
