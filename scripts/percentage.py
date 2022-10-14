# percentage calculator

number = input("Hello: What number would you like to find the percentage today?\n") 

print ("Great, now what percentage of " + number + " are you looking to find today?\n")

percentage = input()

real_percentage= int(percentage) * .01

percentage_ans = int(number) * real_percentage

print("\nHere is your answer - " + str(percentage_ans))
