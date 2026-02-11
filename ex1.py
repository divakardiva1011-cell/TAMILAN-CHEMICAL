student_list=[]
num = int(input("Enter no. of students: "))
for i in range(1,num+1):
 rollno = int(input("Enter Roll Number: "))
 name = input ("Enter Name: ")
 dept = input("Enter Department: ")
 branch = input("Enter Branch: ")
 percentage = float(input("Enter Percentage of Marks: "))
 student_det = [rollno, name, dept, branch, percentage]
 student_list.append(student_det)
print("\nStudent Details (List):")
for i in student_list:
 print("Roll No:", i[0])
 print("Name:", i[1])
 print("Department:", i[2])
 print("Branch:", i[3])
 print("Percentage:", i[4])