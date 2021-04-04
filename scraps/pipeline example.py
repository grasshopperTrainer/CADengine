from pipeline import Pipeline, comp

pipeline = Pipeline()
a = comp.Integer(10)
b = comp.Integer(5)
addition = comp.Add()
pipeline.relate(a, a.value_out, addition.f, addition)
pipeline.relate(b, b.value_out, addition.custom_arg, addition)

pipeline.calculate()
print(addition.vlaue_out)