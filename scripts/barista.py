#!/usr/bin/env python3

#Barista Script

#Made my David Elgut on 09/27/22
#Last Updated on 10/13/22

print ("Hello, welcome to the Graylog Coffee Co.")


#asking our customers for their name, and adding a line break
name = input ( "What is your name?\n" )


#Greeting our customers, and inserting 2 line breaks for better appearance when running the code
print( "Hello " + name + ", thanks for coming in today.\n\n")


#if statement that will determine whether the user will go to the front of the line or not, based on their beard length
beard_length = int(input("how many inches is your beard\n"))

if beard_length >= 1:
    print ("Great! You may skip to the front of the line\n")

else:
    print ("Keep moving beardless human")
    
# These are the menu's that our users will be choosing from
menu = "Cold Brew, Black Coffee, Espresso, Latte, Croissant, Cappuccino, or Frappuccino"
drink_menu = "Cold Brew, Black coffee, Espresso, Latte, Cappuccino, or Frappuccino"

# This is where we are calling the name that was given to the program by the user, as well as calling the menu variable that was listed above
print ("So, " + name + ", what would you like from our menu today? Here is our menu:\n\n" + menu)


# the input statement that will determine price
order = input()


# Here is where we are setting the prices of the different drinks, using if/else and elif statments, and where we are calling the order variable above, and assigning them a dollar amount that is represented by an integer
if order == "Cold Brew":
    price = 7
elif order == "Black Coffee":
    price = 2
elif order == "Espresso":
    price = 5
elif order == "Latte":
    price = 5
# here we are creating some nested if and elif statements to create further depth to our user's ordering experience
elif order == "Croissant":
    question = input("Would you like a coffee with that?\n")
    if question == "yes":
        print ("Here is our menu " + drink_menu)
        drink_and_croissant = input ("What is your choice?\n")
        if drink_and_croissant == "Cold Brew":
            price = 10
        elif drink_and_croissant == "Black Coffee":
            price = 5
        elif drink_and_croissant == "Espresso":
            price = 8
        elif drink_and_croissant == "Latte":
            price = 8
        elif drink_and_croissant == "Cappuccino":
            price = 9
        elif drink_and_croissant == "Frappuccino":
            #here we took the whipped variable that we used below, and used it here for the same options as when a user is order a normal frappuccino
            whipped = input("Would you like whipped cream with that\n")
            if whipped == "yes" or whipped == "YES" or whipped == "yeah" or whipped == "yes please" or whipped == "yea":
                price = 15
            else:
                price = 14
        else:
            print("Sorry, that is not on our coffee menu.\n")
            exit()
    else:
        question == "no"  or question == "nope" or question == "nah" or question == "no thanks" or question == "no thank you"
        price = 3
elif order == "Cappuccino":
    price = 6
elif order == "Frappuccino":
    price = 9
    whipped = input("would you like whipped cream with that\n")
    if whipped == "yes":
        price = 11
    else:
        price = 9 
else:
    print( "sorry, we don't have any of that here")
    exit()

#This is where we are creating value for our variable "quantity"
quantity = input("how many " + order + "'s would you like today?\n")



#the variable "total" becomes our equation to figure out our total price based off of the quantity that was chosen, we also had to make the variable "quantity" an integer so our equation didn't break
total = price * int(quantity)


# Making our "total" variable a string here so that it doesn't break
dollars= str(total)


# Here our milk variable represents what the user will be adding to their milk

milk = "Whole Milk, 2% Milk, Half-and-half, Oatmilk, Almond Milk, Skim Milk"


#statement that calls the milk variable that is displayed to user
print( "What kind of milk would you like with that? These are the options that we have:\n\n" + milk )



#this variable is used to display what the user orders
milk_order=input()

# if and elif used to give extra value to the more expensive milk options
if milk_order == "Oatmilk":
    milk_price = 2
elif milk_order == "Almond Milk":
    milk_price = 1
elif milk_order == "Skim Milk":
    milk_price = 1
elif milk_order == "Whole Milk" or milk_order == "2% Milk" or milk_order == "Half-and-half":
    milk_price = 0
else:
    print("sorry, we don't have any of that")
    exit()
#Equation to add the expensive milk additions to the "total" variable above
actual_total= (total)+ (milk_price * int(quantity))

#converting this to a string so that we can concatenate below
milk_and_coffee_total= str(actual_total)

#if / elif statement so that we can give 2 different responses to our user based off of the amount of drinks they order
if int(quantity) > 1:
    print ("Sounds good! " + name + ", we will have your " + quantity + " " + order + "'s with " + milk_order + " coming right up!\n")

else:
    print ("Sounds good! " + name + ", we will have your " + quantity + " " + order + " with " + milk_order + " coming right up!\n")


#print the total for the customer's total
print ("Aaaaaaannnnndddd, your total is $" + milk_and_coffee_total + " dollars\n")



#giving the option for cash or card
c_or_c = input("Will that be cash or card?\n")


#if / elif statement to give two different responses based on the variable c_or_c
if c_or_c == "cash":
    input("Would you like to donate your change to charity?\n")
elif c_or_c == "card":
    print ("insert or tap your card please")

print ("Well great, thanks for coming to the Graylog Coffee Co. Come back again any time!")
