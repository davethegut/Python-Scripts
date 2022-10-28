#!/usr/bin/env python3

# percentage calculator
# Created by David Elgut
# Date Created 10/14/22
# Last Updated 10/14/22

number = input("Hello: What number would you like to find the percentage today?\n") 

print ("Great, now what percentage of " + number + " are you looking to find today?\n")

percentage = input()

real_percentage= int(percentage) * .01

percentage_ans = int(number) * real_percentage

print("\nHere is your answer - " + str(percentage_ans))
