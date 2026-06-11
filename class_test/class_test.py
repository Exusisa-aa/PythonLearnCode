class Student:
    hand = 2
    leg = 2
    head = 1

    def __init__(self,name,age,sex,hobby):
        self.name = name
        self.age = age
        self.sex = sex
        self.hobby = hobby

    def __str__(self):
        return f"{self.name} is {self.age} years old,sex is {self.sex},hobby is {self.hobby}"

    def __eq__(self, other):
        return self.name == other.name and self.age == other.age and self.sex == other.sex

    def running(self):
        print(f"{self.name} is running~~")

    def doingHobby(self,time):
        print(f"{self.name}在{time}点正在{self.hobby}")


if __name__ == '__main__':
    s1 = Student("张三",20,"男","打篮球")
    print(s1.__dict__)
    s1.running()
    s1.doingHobby("10:00")


    s2 = Student("张三",20,"男","踢足球")
    print(s2)
    print(s1 == s2)

    print(s1.leg)
    print(s1.head)
