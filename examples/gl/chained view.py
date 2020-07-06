from UVT.env.MVC.view import View

a = View(0, 10, 100, 100, None)
b = View(0, 0.5, lambda x: x-20, 0.5, a)

print(b.x, b.y, b.w, b.h)
a.y = 20
print(b.x, b.y, b.w, b.h)
