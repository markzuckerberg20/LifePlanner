
import pandas as pd
from flask import Flask, flash, send_from_directory, render_template, request, redirect, url_for, jsonify, session, Response
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import plotly.io as pio
import os
import io
from datetime import datetime

# Load the tax data from the Excel file
file_path = 'mysite/TaxesZH.csv'
tax_data = pd.read_csv(file_path)

app = Flask(__name__)
app.secret_key = '0123456789'

# Helper function to set session variables from form data
def set_session_data(request, keys, types=None):
    for key in keys:
        value = request.form.get(key, None)
        if types and key in types:
            try:
                value = types[key](value) if value else None
            except ValueError:
                value = None
        session[key] = value

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route for General Information
@app.route('/general', methods=['GET', 'POST'])
def general():
    if request.method == 'POST':
        # Collect form data
        gross_salary = request.form.get('gross_salary', type=float)
        # print(f"Gross Salary: {gross_salary}")
        wealth = request.form.get('wealth', type=float)
        age = request.form.get('age', type=int)
        location = request.form.get('location', type=str)
        retirement_age = request.form.get('retirement_age', type=int)



        # Store in session
        session['gross_salary'] = gross_salary
        session['wealth'] = wealth
        session['age'] = age
        session['location'] = location
        session['retirement_age'] = retirement_age

        # Redirect to the next page
        return redirect(url_for('overview'))
    
    # Render the template with the existing session data if available
    return render_template(
        'general.html',
        gross_salary=session.get('gross_salary'),
        wealth=session.get('wealth'),
        age=session.get('age'),
        location=session.get('location'),
        retirement_age=session.get('retirement_age')
    )
# Route for Choices (Decision Tree)
@app.route('/overview')
def overview():
    return render_template('overview.html')

# Route for Living details
@app.route('/living', methods=['GET', 'POST'])
def living():
    if request.method == 'POST':

        environment = request.form.get('environment', type=str)
        living_choice = request.form.get('living_choice', type=str)
        age_to_buy = request.form.get('age_to_buy', type=int)
        house_type = request.form.get('type', type=str)
        space = request.form.get('space', type=int)
        dimension = request.form.get('dimension', type=str)

        # Store in session
        session['environment'] = environment
        session['living_choice'] = living_choice
        session['age_to_buy'] = age_to_buy
        session['type'] = house_type
        session['space'] = space
        session['dimension'] = dimension

        if not all([environment, living_choice, age_to_buy, house_type, space, dimension]):
            flash("Please fill out all required fields in the Living section.")
            return render_template('living.html')  # Rerender with a warning

        return redirect(url_for('overview'))
    return render_template('living.html',
                           environment=session.get('environment'),
                           living_choice=session.get('living_choice'),
                           age_to_buy=session.get('age_to_buy'),
                           house_type=session.get('type'),
                           space=session.get('space'),
                           dimension=session.get('dimension'))

# Additional routes for Children, Luxus, and Pension pages
@app.route('/children', methods=['GET', 'POST'])
def children():
    if request.method == 'POST':
        session['wants_children'] = request.form.get('wants_children')
        session['already_have_children'] = request.form.get('already_have_children')
        session['num_children'] = int(request.form.get('num_children', 0))
        session['age_first_child'] = int(request.form.get('age_first_child', 0))
        session['child_age'] = int(request.form.get('child_age', 0))
        return redirect(url_for('overview'))
    return render_template('children.html',
                           wants_children=session.get('wants_children'),
                           already_have_children=session.get('already_have_children'),
                           num_children=session.get('num_children'),
                           age_first_child=session.get('age_first_child'),
                           child_age=session.get('child_age'))

@app.route('/luxury', methods=['GET', 'POST'])
def luxury():
    if request.method == 'POST':
        # session['wants_luxury'] = request.form.get('wants_luxury')

        session['age_car'] = request.form.get('age_car')
        session['car_attributes'] = request.form.get('car_attributes')  # Values can be "Medium", "Mid_luxury", "Luxury", "Sport"
        session['age_travel'] = request.form.get('age_travel')
        session['travel_attributes'] = request.form.get('travel_attributes')
        session['age_watch'] = request.form.get('age_watch')
        session['watch_attributes'] = request.form.get('watch_attributes')
        session['age_wedding'] = request.form.get('age_wedding')
        session['wedding_attributes'] = request.form.get('wedding_attributes')
        session['age_other'] = request.form.get('age_other')
        session['other_attributes'] = request.form.get('other_attributes')

        return redirect(url_for('overview'))
    
    return render_template('luxury.html',
                           age_car=session.get('age_car'),
                           car_attributes=session.get('car_attributes'),
                           age_travel=session.get('age_travel'),
                           travel_attributes=session.get('travel_attributes'),
                           age_watch=session.get('age_watch'),
                           watch_attributes=session.get('watch_attributes'),
                           age_wedding=session.get('age_wedding'),
                           wedding_attributes=session.get('wedding_attributes'),
                           age_other=session.get('age_other'),
                           other_attributes=session.get('other_attributes'))

def interst_rate_investments(age_at_purchase):

    current_age = session.get('age')

    years_to_save = age_at_purchase - current_age

    if years_to_save < 2:
        return 0.005
    elif 2 <= years_to_save < 5:
        return 0.02
    elif 5 <= years_to_save < 10:
        return 0.04
    else:
        return 0.06

def calculate_savings_summary(savings_list):
    
    current_age = int(session.get('age'))
    car_age = int(session.get('age_car'))

    car_savings_list = calculate_car_savings()
    return_rate = interst_rate_investments(car_age)
    # Determine the interest rate based on years to save
    years_to_save = car_age - current_age

    # Calculate the total present value (PV)
    total_car_cost = sum(yearly_savings for _, yearly_savings in savings_list)

    # Calculate the yearly savings required without interest
    if years_to_save > 0:
        yearly_savings_without_return = total_car_cost / years_to_save
    else:
        yearly_savings_without_return = 0

    # Calculate the yearly savings required considering the return rate
    if years_to_save > 0:
        sum_of_discounts = sum(1 / (1 + return_rate) ** t for t in range(1, years_to_save + 1))
        yearly_savings_with_return = total_car_cost / sum_of_discounts
    else:
        yearly_savings_with_return = 0

    # Calculate the difference between the two savings amounts
    savings_difference = yearly_savings_with_return - yearly_savings_without_return

    accumulated_savings_list = []
    for age, _ in savings_list:
        accumulated_savings_list.append((age, savings_difference if age < car_age else 0))

   # print(f"Yearly Accumulated Savings for car: {accumulated_savings_list}")
    #print(f"Yearly Savings Without Return: {yearly_savings_without_return}")
    #print(f"Yearly Savings With Return: {yearly_savings_with_return}")
   # print(f"Savings Difference (Benefit of Investing): {savings_difference}")

    return accumulated_savings_list

def calculate_car_price(car_type):
    
    if car_type == 'Mid':
        car_price = 30000
    elif car_type == 'Mid_Luxury':
        car_price = 45000
    elif car_type == 'Luxury':
        car_price = 100000
    elif car_type == 'Sport':
     car_price = 120000
    else:
        car_price = 0

    return car_price

def calculate_car_savings():

    current_age = int(session.get('age'))
    age_car = session.get('age_car')
    car_type = session.get('car_attributes')

    if age_car is not None:
        age_car = float(age_car)
    else:
        print("Error: 'age_car' is missing")
        return []

    #print(f"Age of purchase: {age_car}")
    #print(f"Car Type: {car_type}")
    car_price = calculate_car_price(car_type)

    savings_per_year = 0

    if car_price > 0 and age_car > current_age:
            years_to_save = int(age_car) - current_age
            savings_per_year = car_price / years_to_save
    
    #print(f"savings per year (car): {savings_per_year}")

    car_saving_list = []
    for age in range(current_age, 81):
        if age < age_car:
            car_saving_list.append((age, savings_per_year))  # No savings before purchase age
        else:
            car_saving_list.append((age, 0))

    #print(f"Car Savings: {car_saving_list}")
    return car_saving_list

def calculate_travel_price(travel_type):

    if travel_type == 'Low_budgetE':
        vacation_price = 2000
    elif travel_type == 'All_inclusiveO':
        vacation_price = 7000
    elif travel_type == 'Low_budgetO':
        vacation_price = 3000
    elif travel_type == 'All_inclusiveE':
        vacation_price = 4000
    else:
        vacation_price = 0
    
    return vacation_price


def calculate_travel_savings():

    current_age = int(session.get('age'))
    vacation_age = session.get('age_travel')
    travel_type = session.get('travel_attributes')

    if vacation_age is not None:
        vacation_age = float(vacation_age)
    else:
        print("Error: 'vacation_age' is missing")
        return []

    #print(f"Age of purchase: {vacation_age}")
   # print(f"Vacation Type: {travel_type}")
    vacation_price = calculate_travel_price(travel_type)

    savings_per_year = 0

    if vacation_price > 0 and vacation_age > current_age:
            years_to_save = int(vacation_age) - current_age
            savings_per_year = vacation_price / years_to_save
    
    #print(f"savings per year (vacation): {savings_per_year}")

    vacation_saving_list = []
    for age in range(current_age, 81):
        if age < vacation_age:
            vacation_saving_list.append((age, savings_per_year))  # No savings before purchase age
        else:
            vacation_saving_list.append((age, 0))

    #print(f"Car Savings: {vacation_saving_list}")
    return vacation_saving_list

def calculate_watch_price(watch_type):
    if watch_type == 'Mid':
        watch_price = 2000
    elif watch_type == 'High':
        watch_price = 80000
    elif watch_type == 'Luxury':
        watch_price = 15000
    else:
        watch_price = 0
    
    return watch_price


def calculate_watch_savings():

    current_age = int(session.get('age'))
    watch_age = session.get('age_watch')
    watch_type = session.get('watch_attributes')

    if watch_age is not None:
        watch_age = float(watch_age)
    else:
        print("Error: 'watch_age' is missing")
        return []

    #print(f"Age of purchase: {watch_age}")
    #print(f"Watch Type: {watch_type}")

    watch_price = calculate_watch_price(watch_type)
    
    savings_per_year = 0

    if watch_price > 0 and watch_age > current_age:
            years_to_save = int(watch_age) - current_age
            savings_per_year = watch_price / years_to_save
    
    #print(f"savings per year (watch): {savings_per_year}")

    watch_saving_list = []
    for age in range(current_age, 81):
        if age < watch_age:
            watch_saving_list.append((age, savings_per_year))  # No savings before purchase age
        else:
            watch_saving_list.append((age, 0))

    #print(f"Watch Savings: {watch_saving_list}")
    return watch_saving_list

def calculate_wedding_price(wedding_type):
    if wedding_type == 'Normal':
        wedding_price = 10000
    elif wedding_type == 'Mid':
        wedding_price = 35000
    elif wedding_type == 'Expensive':
        wedding_price = 60000
    else:
        wedding_price = 0

    return wedding_price

def calculate_wedding_savings():

    current_age = int(session.get('age'))
    wedding_age = session.get('age_wedding')
    wedding_type = session.get('wedding_attributes')

    if wedding_age is not None:
        wedding_age = float(wedding_age)
    else:
        print("Error: 'wedding_age' is missing")
        return []

    #print(f"Age of purchase: {wedding_age}")
    #print(f"Wedding Type: {wedding_type}")
    wedding_price = calculate_wedding_price(wedding_type)
    savings_per_year = 0

    if wedding_price > 0 and wedding_age > current_age:
            years_to_save = int(wedding_age) - current_age
            savings_per_year = wedding_price / years_to_save
    
    #print(f"savings per year (wedding): {savings_per_year}")

    wedding_saving_list = []
    for age in range(current_age, 81):
        if age < wedding_age:
            wedding_saving_list.append((age, savings_per_year))  # No savings before purchase age
        else:
            wedding_saving_list.append((age, 0))

    #print(f"Wedding Savings: {wedding_saving_list}")
    return wedding_saving_list

def calculate_other_savings():

    current_age = int(session.get('age'))
    other_age = session.get('age_other')
    other_type = session.get('other_attributes')

    if other_age is not None:
        try:
            other_age = float(other_age)
        except ValueError:
            print("Error: 'other_age' is not a valid number")
            return []
    else:
        print("Error: 'other_age' is missing")
        return []

    try:
        other_price = float(other_type) if other_type is not None else 0
    except ValueError: 
        print("Error: 'other attributes' is not a valid number")
        return []
 
    #print(f"Age of other purchase: {other_age}")
    #print(f"Other: {other_type}")

    savings_per_year = 0

    if other_price > 0 and other_age > current_age:
            years_to_save = int(other_age) - current_age
            savings_per_year = other_price / years_to_save
    
    #print(f"savings per year (other): {savings_per_year}")

    other_saving_list = []
    for age in range(current_age, 81):
        if age < other_age:
            other_saving_list.append((age, savings_per_year))  # No savings before purchase age
        else:
            other_saving_list.append((age, 0))

    #print(f"Wedding Savings: {other_saving_list}")
    return other_saving_list

def find_house_price():
    # Get user inputs from session
    current_age = session.get('age')
    space = session.get('space')  
    purchase_age = session.get('age_to_buy')
    property_type = session.get('type')  # house or flat
    location = session.get('environment')  # countryside or city
    dimension = session.get('dimension')  #cheap, normal, expensive

    if None in [current_age, space, purchase_age, property_type, location, dimension]:
        raise ValueError("One or more required inputs are missing from the session.")

    # Base prices based on dimension
    base_prices = {
        'normal': 300000,
        'medium': 900000,
        'luxury': 2000000
    }

    # Price adjustments
    property_type_multiplier = 1.0 if property_type == 'house' else 0.8  # Flats are generally cheaper
    location_multiplier = 1.2 if location == 'urban' else 1.0  # City is more expensive
    size_price_per_sqm = 9960  # Updated price per square meter for a house

    # Calculate the initial price based on user inputs
    base_price = base_prices.get(dimension, 300000)  # Default to 'normal' if dimension is not found
    size_price = space * size_price_per_sqm
    initial_price = base_price * property_type_multiplier * location_multiplier + size_price

    # Assuming house price increases over time, we can set a growth rate
    annual_growth_rate = 0.03  # 3% annual growth rate

    # Create a list of tuples (age, house price)
    house_price_list = []
    for age in range(current_age, 81):
        if age < purchase_age:
            house_price_list.append((age, 0))  # No house before purchase age
        else:
            years_since_purchase = age - purchase_age
            house_price = initial_price * ((1 + annual_growth_rate) ** years_since_purchase)
            house_price_list.append((age, house_price))

    print(f"House Prices: {house_price_list}")
    return house_price_list

from flask import session

def find_house_price2():
    # Get user inputs from session
    current_age = session.get('age')
    space = session.get('space')  
    purchase_age = session.get('age_to_buy')
    property_type = session.get('type')  # house or flat
    location = session.get('environment')  # countryside or city
    dimension = session.get('dimension')  # cheap, normal, medium, luxury

    # Check if all required inputs are present
    if None in [current_age, space, purchase_age, property_type, location, dimension]:
        raise ValueError("One or more required inputs are missing from the session.")

    # Base prices based on dimension
    base_prices = {
        'normal': 300000,
        'medium': 900000,
        'luxury': 2000000
    }

    # Price adjustments
    property_type_multiplier = 1.0 if property_type == 'house' else 0.8  # Flats are generally cheaper
    location_multiplier = 1.2 if location == 'urban' else 1.0  # City is more expensive
    size_price_per_sqm = 9960  # Updated price per square meter for a house

    # Calculate the initial price based on user inputs
    base_price = base_prices.get(dimension, 300000)  # Default to 'normal' if dimension is not found
    size_price = space * size_price_per_sqm
    initial_price = base_price * property_type_multiplier * location_multiplier + size_price

    # Assuming house price increases over time, set a growth rate
    annual_growth_rate = 0.03  # 3% annual growth rate

    # Create a list of tuples (age, house price) from current_age until purchase_age
    house_price_list = []
    current_price = initial_price

    for age in range(current_age, purchase_age + 1):
        house_price_list.append((age, current_price))

        # Increment the price each year by the growth rate
        current_price *= (1 + annual_growth_rate)

    # Print for debugging
    print(f"House Prices from {current_age} to {purchase_age}: {house_price_list}")

    # Return the house price list (price projected until purchase age)
    return house_price_list


def calculate_mortgage_payment(house_price_list, interest_rate=0.04, mortgage_term=30):
    # Get the current age from session
    current_age = session.get('age')
    if current_age is None:
        raise ValueError("Current age is not provided in the session.")

    # Create a list of tuples (age, mortgage payment)
    mortgage_payment_list = []
    for age, house_price in house_price_list:
        if age > current_age + mortgage_term:
            break  # Stop calculating payments after the mortgage term ends

        if house_price == 0:
            mortgage_payment_list.append((age, 0))  # No payment before the house is purchased
            continue

        # Calculate the monthly mortgage payment using the formula for an amortizing loan
        monthly_interest_rate = interest_rate / 12
        number_of_payments = mortgage_term * 12
        monthly_payment = (house_price * monthly_interest_rate) / (1 - (1 + monthly_interest_rate) ** -number_of_payments)
        annual_payment = monthly_payment * 12

        mortgage_payment_list.append((age, annual_payment))

    #print(f"Mortgage Payments: {mortgage_payment_list}")
    return mortgage_payment_list

def calculate_annual_house_savings():
    # Get user inputs from session
    current_age = session.get('age')
    purchase_age = session.get('age_to_buy')
    if None in [current_age, purchase_age]:
        raise ValueError("Current age or purchase age is not provided in the session.")

    # Get the house price list
    house_price_list = find_house_price()
    
    # Find the house price at the purchase age
    house_price_at_purchase = next((price for age, price in house_price_list if age == purchase_age), None)
    if house_price_at_purchase is None:
        raise ValueError("House price at purchase age could not be determined.")

    # Calculate the down payment needed (20% of the house price)
    down_payment_needed = 0.2 * house_price_at_purchase

    # Calculate the number of years to save
    years_to_save = purchase_age - current_age
    if years_to_save <= 0:
        raise ValueError("Purchase age must be greater than the current age.")

    # Calculate the annual savings needed (considering 4% interest)
    interest_rate = 0.04
    annual_savings_needed = down_payment_needed / sum([(1 + interest_rate) ** (-i) for i in range(1, years_to_save + 1)])

    #print(f"Annual Savings Needed: {annual_savings_needed}")
    return annual_savings_needed

def calculate_health_insurance():
    # Get the current age from session
    current_age = session.get('age')
    if current_age is None:
        raise ValueError("Current age is not provided in the session.")

    # Initial health insurance value (assuming user provides it through session as well)
    health_insurance = 3954.57

    # Create list of tuples for ages and health insurance values
    h_insurance_list = []
    for age in range(current_age, 81):
        h_insurance_list.append((age, round(health_insurance, 2)))
        health_insurance *= 1.0201  # Increase health insurance value by 2.01%

    #print(f"Health Insurance: {h_insurance_list}")

    return h_insurance_list

def running_costs():

    gross_salary = session.get('gross_salary')
    current_age = session.get('age')

    if gross_salary <= 56028:
        run_costs = gross_salary * 0.37
    elif 56028 < gross_salary <= 84048:
        run_costs = gross_salary * 0.36
    elif 84048 < gross_salary <= 116796:
        run_costs = gross_salary * 0.33
    elif 116796 < gross_salary <= 164604:
        run_costs = gross_salary * 0.31
    elif gross_salary > 164604:
        run_costs = gross_salary * 0.29

    running_c_list = []

    for age in range(current_age, 81):
        running_c_list.append((age, run_costs))
    
    return running_c_list 

def renting_costs():
    gross_salary = session.get('gross_salary')
    current_age = session.get('age')

    if gross_salary <= 56028:
        rent_costs = gross_salary * 0.23
    elif 56028 < gross_salary <= 84048:
        rent_costs = gross_salary * 0.18
    elif 84048 < gross_salary <= 116796:
        rent_costs = gross_salary * 0.15
    elif 116796 < gross_salary <= 164604:
        rent_costs = gross_salary * 0.12
    elif gross_salary > 164604:
        rent_costs = gross_salary * 0.12

    rent_c_list = []

    for age in range(current_age, 81):
        rent_c_list.append((age, rent_costs))
    
    return rent_c_list

def calculate_child_costs():
    # Get current age, planned age for the first child, gross salary, and number of kids from the session
    current_age = session.get('age', 0)
    first_child_age = session.get('age_first_child', 0)
    gross_salary = session.get('gross_salary', 0)
    num_children = session.get('num_children', 1)

    # Set the base cost
    base_cost = 10000

    # Adjust the base cost based on gross salary
    if gross_salary > 0:
        # Assume the cost scales proportionally to the salary, with a factor of 30% of the gross salary
        adjustment_factor = 0.3
        adjusted_cost = base_cost * (1 + (adjustment_factor * (gross_salary / 100000)))
    else:
        adjusted_cost = base_cost

    # Create an empty list to store age and cost tuples
    age_cost_list = []

    for child_index in range(num_children):
        child_start_age = first_child_age + (child_index * 2)  # Assuming a 2-year gap between each child
        child_end_age = child_start_age + 18  # Cost ends when the child turns 18

        for age in range(child_start_age, child_end_age + 1):
            child_age = age - child_start_age
            if 0 <= child_age <= 4:
                age_factor = 0.9
            elif 5 <= child_age <= 12:
                age_factor = 1.0
            elif 13 <= child_age <= 18:
                age_factor = 1.2
            else:
                age_factor = 1.0

            # First child has full cost, subsequent children have reduced cost
            weight = 1.0 if child_index == 0 else 0.7

            cost = adjusted_cost * weight * age_factor

            # Add or update the cost for the given age
            existing_entry = next((entry for entry in age_cost_list if entry[0] == age), None)
            if existing_entry:
                age_cost_list = [(a, c + cost) if a == age else (a, c) for a, c in age_cost_list]
            else:
                age_cost_list.append((age, cost))
    
    return age_cost_list

def calculate_total_costs():
    # Get current age from session
    current_age = session.get('age')
    if current_age is None:
        raise ValueError("Current age is not provided in the session.")

    # Get lists of costs from individual functions
    health_insurance_list = calculate_health_insurance()
    running_costs_list = running_costs()
    renting_costs_list = renting_costs()
    child_costs_list = calculate_child_costs()

    # Create a dictionary to accumulate costs for each age
    total_costs_dict = {}
    for cost_list in [health_insurance_list, running_costs_list, renting_costs_list, child_costs_list]:
        for age, cost in cost_list:
            if age not in total_costs_dict:
                total_costs_dict[age] = 0
            total_costs_dict[age] += cost

    # Create a list of tuples (age, total costs)
    total_costs_list = [(age, total_costs_dict[age]) for age in range(current_age, 81)]
    #print(f" Total Cost: {total_costs_list}")

    return total_costs_list

# Function to calculate projected salary growth
def calculate_salary_projection(gross_salary, current_age, retirement_age, inflation_rate=0.005, salary_increase_rate=0.007):

    gross_salary = session.get('gross_salary')
    current_age = session.get('age')
    retirement_age = session.get('retirement_age')

    if gross_salary is None:
        raise ValueError("Gross salary cannot be None")
    if inflation_rate is None:
        raise ValueError("Inflation rate cannot be None")
    if salary_increase_rate is None:
        raise ValueError("Salary increase rate cannot be None")

    projection = []
    for age in range(current_age, retirement_age + 1):
        projection.append((age, gross_salary))
        gross_salary *= (1 + inflation_rate + salary_increase_rate)
    return projection

def calculate_terminal_projection():

    gross_salary = session.get('gross_salary')
    current_age = session.get('age')
    retirement_age = session.get('retirement_age', 65)
    location = session.get('location')

    
    projected_salary = calculate_salary_projection(gross_salary, current_age, retirement_age) # (age, salary with inflation/growth)
    salary_after_pension = calculate_pension_deductions(projected_salary) # (age, projected salary minus pension deductions)
    federal_tax = calculate_federal_tax(salary_after_pension) # (age, federal tax based on salary after deductions)
    cantonal_tax = calculate_cantonal_tax(salary_after_pension) # (age, cantonal taxes based on salary afer deductions)
    munic_canton_tax = calculate_munic_canton_tax(location) # (canton tax rate) (municipality tax rate)
    final_projections = get_tax_rates() # (age, salary after taxes and deduction)

    # We need: 

    retirement_payment = calculate_retirement_asset(projected_salary)

    pension_payments_list = [(age, retirement_payment) for age in range(retirement_age, 81)]
  
    final_list = final_projections + pension_payments_list

    return final_list

    
def calculate_pension_deductions(salary_projection):
    """
    Calculates the income after pension deductions for each year in the salary projection.

    Parameters:
        salary_projection (list of tuples): List of tuples [(age, salary), ...].

    Returns:
        list of tuples: [(age, income_after_pension), ...]
    """
    income_after_pension_projections = []

    for age, salary in salary_projection:
        # Determine retirement credit rate inline
        if 25 <= age <= 34:
            retirement_credit_rate = 0.07
        elif 35 <= age <= 44:
            retirement_credit_rate = 0.10
        elif 45 <= age <= 54:
            retirement_credit_rate = 0.15
        elif 55 <= age <= 65:
            retirement_credit_rate = 0.18
        else:
            retirement_credit_rate = 0.0

        # First pillar deduction
        first_pillar_deduction = salary * 0.079

        # Second pillar deductions
        second_pillar_base = max((salary - 26460), 0)
        additional = max((second_pillar_base - 88200), 0)
        second_pillar_deduction = ((second_pillar_base + additional) * retirement_credit_rate)

        # Total pension deduction
        total_pension_deduction = first_pillar_deduction + (second_pillar_deduction * 0.5)

        # Calculate income after pension deductions
        income_after_pension = salary - total_pension_deduction
        # print(f"1st pillar: {first_pillar_deduction}")
        # print(f"2nd pillar: {second_pillar_deduction}")
        # Append as tuple
        income_after_pension_projections.append((age, income_after_pension))

    return income_after_pension_projections

# output of retirement_payments is the annual payment in reitrement (bsp 80'000)
def calculate_retirement_asset(salary_projection):
    """
    Calculates the total sum of all second pillar deductions with an annual interest rate of 1.25%.

    Parameters:
        second_pillar_deductions (list of floats): List of second pillar deductions for each year.

    Returns:
        float: Total sum of second pillar deductions with interest applied.
    """
    second_pillar_deductions = []

    for age, salary in salary_projection:
        # Determine retirement credit rate inline
        if 25 <= age <= 34:
            retirement_credit_rate = 0.07
        elif 35 <= age <= 44:
            retirement_credit_rate = 0.10
        elif 45 <= age <= 54:
            retirement_credit_rate = 0.15
        elif 55 <= age <= 64:
            retirement_credit_rate = 0.18
        else:
            retirement_credit_rate = 0.0

        # Second pillar deductions
        second_pillar_base = max((salary - 26460), 0)
        additional = max((second_pillar_base - 88200), 0)
        second_pillar_deduction = ((second_pillar_base + additional) * retirement_credit_rate)
        second_pillar_deductions.append(second_pillar_deduction) 

    total_sum = 0.0
    for deduction in second_pillar_deductions:
        total_sum = (total_sum + deduction) * 1.0125

    retirement_payments = (total_sum * 0.068) + (2520 * 13)

    # print(f"retirement_payments: {retirement_payments}")

    return retirement_payments

def calculate_federal_tax(taxable_income_list):
    """
    Calculates federal tax based on taxable income.

    Parameters:
        taxable_income (float): Taxable income.

    Returns:
        float: Federal tax amount.
    """
    
    brackets = [
        (32800, 0.0, 0.0077),
        (42900, 137.05, 0.0077),
        (57200, 225.9, 0.0088),
        (75200, 603.4, 0.0264),
        (81000, 1138, 0.0297),
        (107400, 1482.5, 0.0594),
        (139600, 3254.9, 0.066),
        (182600, 6058, 0.088),
        (783200, 10788.5, 0.11),
        (1000000, 90067, 0.13),
    ]
    federal_tax = []

    for age, adjusted_income in taxable_income_list:
        tax = 0
        previous_limit = 0
        for limit, fixed_tax, rate in brackets:
            if adjusted_income <= limit:
                tax = fixed_tax + (adjusted_income - previous_limit) * rate
                break
            previous_limit = limit

        federal_tax.append((age, tax))

    return federal_tax

def calculate_cantonal_tax(taxable_income_list):
    """
    Calculates cantonal tax based on taxable income.

    Parameters:
        taxable_income (float): Taxable income.

    Returns:
        float: Cantonal tax amount.
    """

    brackets = [
        (11800, 0, 2.00),
        (16600, 98, 3.00),
        (24500, 242, 4.00),
        (34100, 558, 5.00),
        (45100, 1038, 6.00),
        (58000, 1698, 7.00),
        (75400, 2601, 8.00),
        (109000, 3993, 9.00),
        (142200, 7017, 10.00),
        (194900, 10337, 11.00),
        (263300, 16134, 12.00),
        (500000, 23342, 13.00),
    ]
    canton_tax = []

    for age, adjusted_income in taxable_income_list:
        tax = 0
        previous_limit = 0
        for limit, fixed_tax, rate in brackets:
            if adjusted_income <= limit:
                tax = fixed_tax + (adjusted_income - previous_limit) * (rate / 100)
                break
            previous_limit = limit

        canton_tax.append((age, tax))

    return canton_tax


def calculate_munic_canton_tax(location):

    location = session.get('location')

    # Filter tax data based on user location (municipality) or postcode
    location = location.strip().lower()
    tax_data['Municipality'] = tax_data['Municipality'].str.strip().str.lower()
    tax_info = tax_data[tax_data['Municipality'] == location]
    
    # Check if there are any matching rows
    if not tax_info.empty:
        # Retrieve tax rates from the matched row
        income_tax_canton = tax_info.iloc[0]['Income tax canton']
        income_tax_municipality = tax_info.iloc[0]['Income tax municipality']
        # print(f"Income Tax Municipality: {income_tax_municipality}")
        # print(f"Income Tax canton: {income_tax_canton}")
        return income_tax_canton, income_tax_municipality
    else:
        # Handle the case where no match is found
        print(f"No matching municipality found for location: {location}")
        return "No matching municipality found. Please provide a valid location."


# Function to get tax rates for a specific municipality
def get_tax_rates():

    gross_salary = session.get('gross_salary')
    age = session.get('age')
    retirement_age = session.get('retirement_age')
    location = session.get('location')

    # Ensure we have all the necessary user information
    if not (gross_salary and age and retirement_age and location):
        return "Missing necessary information. Please go back and fill out the form."

    # Retrieve tax rates and calculate canton and municipality taxes based on location
    tax_info = calculate_munic_canton_tax(location)
    if tax_info is None:
        return "No matching municipality found. Please provide a valid location."
    
    income_tax_canton, income_tax_municipality = tax_info
    

    # Calculate salary projection from current age to retirement age
    salary_projection = calculate_salary_projection(
        gross_salary=gross_salary,
        current_age=age,
        retirement_age=retirement_age
    )

    # Calculate income after pension deductions
    income_after_pension_projection = calculate_pension_deductions(salary_projection)

    federal_tax_projection = {
        age_projection: federal_tax
        for age_projection, federal_tax in calculate_federal_tax(income_after_pension_projection)
    }
    # print(federal_tax_projection)

    cantonal_tax_projection = {
        age_projection: cantonal_tax
        for age_projection, cantonal_tax in calculate_cantonal_tax(income_after_pension_projection)
    }
    final_tax_projections = []

    for (projected_age, income_after_pension) in income_after_pension_projection:
        # Use income_after_pension as adjusted_salary
        adjusted_salary = float(income_after_pension)

        # Calculate income and municipal tax for the current year

        # Calculate federal tax
        federal_tax = federal_tax_projection.get(projected_age, 0)

        cantonal_tax = cantonal_tax_projection.get(projected_age, 0)

        total_tax = federal_tax + cantonal_tax + (cantonal_tax * (income_tax_municipality/100))
        # total_tax = federal_tax + (cantonal_tax * income_tax_canton) + (cantonal_tax * income_tax_canton * income_tax_municipality)
        income_after_tax_and_deductions = adjusted_salary - total_tax

        # Append tuple (age, adjusted_salary, year_tax, federal_tax)
        final_tax_projections.append((projected_age, income_after_tax_and_deductions))

        #print(f"Total Tax: {total_tax}")
        #print(f"Adjusted Salary: {adjusted_salary}")

    return final_tax_projections
   
def calculate_residual_income():
    # Get current age from session
    current_age = session.get('age')
    if current_age is None:
        raise ValueError("Current age is not provided in the session.")

    # Get the lists of income and costs
    income_list = calculate_terminal_projection()  # Assuming this gives (age, income)
    costs_list = calculate_total_costs()  # Assuming this gives (age, total costs)

    # Create dictionaries to make it easy to lookup costs and income by age
    income_dict = dict(income_list)
    costs_dict = dict(costs_list)

    # Create a list of tuples (age, residual income)
    residual_income_list = []
    for age in range(current_age, 81):
        income = income_dict.get(age, 0)  # Get income for the age, default to 0 if not found
        cost = costs_dict.get(age, 0)  # Get cost for the age, default to 0 if not found
        residual_income = income - cost  # Calculate residual income
        residual_income_list.append((age, residual_income))

    #print(f"Residual Income: {residual_income_list}")
    return residual_income_list


# Route for the Results page
@app.route('/results')
def results():
    
    gross_salary = session.get('gross_salary')
    current_age = session.get('age')
    retirement_age = session.get('retirement_age')
    location = session.get('location')
    
    house_purchase_age = session.get('age_to_buy')
    initial_savings = session.get('wealth')

    car_type = session.get('car_attributes')
    car_age = session.get('age_car')

    travel_age = session.get('age_travel')
    travel_type = session.get('travel_attributes')

    watch_age = session.get('age_watch')
    watch_type = session.get('watch_attributes')

    wedding_age = session.get('age_wedding')
    wedding_type = session.get('wedding_attributes')


    projected_salary = calculate_salary_projection(gross_salary, current_age, retirement_age)
    salary_after_pension = calculate_pension_deductions(projected_salary)
    federal_tax = calculate_federal_tax(salary_after_pension)
    cantonal_tax = calculate_cantonal_tax(salary_after_pension)
    munic_canton_tax = calculate_munic_canton_tax(location)
    final_projections = get_tax_rates() #goes only until retirement age
    total_assets = calculate_retirement_asset(projected_salary)
    final_list = calculate_terminal_projection() # goes until
    total_cost_list = calculate_total_costs()
    h_insurance = calculate_health_insurance()
    running_costss = running_costs()
    renting_costss = renting_costs()
    kid_costs = calculate_child_costs()
    residual_income_list = calculate_residual_income()
    hous_price = find_house_price()
    mortgage = calculate_mortgage_payment(hous_price)
    annual_house_savings = calculate_annual_house_savings()
    car_savings = calculate_car_savings()
    travel_savings = calculate_travel_savings()
    watch_savings = calculate_watch_savings()
    wedding_savings = calculate_wedding_savings() 
    other_savings = calculate_other_savings()
    car_savings_with_returns = calculate_savings_summary(car_savings)
    watch_savings_with_returns = calculate_savings_summary(watch_savings)


    #print(f"Projected Salary: {projected_salary}")
    #print(f"Salary minus Pension: {salary_after_pension}")
    print(f"Residual Income: {residual_income_list}")
    #print(f"Final projections: {final_projections}", flush=True)
    #print(f"Taxes: {federal_tax}", flush=True)
    # print(f"Final List: {final_list}", flush=True)
    # print(f"Final list : {total_cost_list}", flush=True)
    # print(f"Health care : {h_insurance}", flush=True)
    # print(f" Running Cost : {running_costss}", flush=True)
    # print(f"rent cost : {renting_costss}", flush=True)
    # print(f"Kids cost : {kid_costs}", flush=True)
    print(f"house price : {hous_price}", flush=True)
    # print(f"Mortgage : {mortgage}", flush=True)
    #print(f"Savings needed for House : {annual_house_savings}", flush=True)
    #print(f"Travel savings: {travel_savings}")
    #print(f"Wedding savings: {watch_savings}")
    #print(f"Watch savings: {wedding_savings}")
    #print(f"Car savings: {car_savings}")
    #print(f"Car savings with returns: {car_savings_with_returns}")
    #print(f"Watch savings with returns: {watch_savings_with_returns}")

    hous_price = find_house_price()
    mortgage = calculate_mortgage_payment(hous_price)
    annual_house_savings = calculate_annual_house_savings()
    hous_price_projection = find_house_price2()

    hous_price_at_buying_age = hous_price_projection[-1][1]
    downpayment = hous_price_at_buying_age * 0.25

    years_until_downpayment = house_purchase_age - current_age

    return_rate = interst_rate_investments(house_purchase_age)

    if years_until_downpayment <= 0:
        annual_savings = downpayment
    else:
        annual_savings = downpayment / years_until_downpayment

    if return_rate > 0 and years_until_downpayment > 0:
        required_annual_savings = downpayment * return_rate / ((1 + return_rate) ** years_until_downpayment - 1)
    else:
        required_annual_savings = downpayment / years_until_downpayment if years_until_downpayment > 0 else downpayment

    if return_rate == 0:
        return initial_savings + annual_house_savings * years_until_downpayment
    else:
        future_value_of_initial_savings = initial_savings * ((1 + return_rate) ** years_until_downpayment)
        future_value_of_annual_savings = annual_savings * (((1 + return_rate) ** years_until_downpayment - 1) / return_rate)

        future_value = future_value_of_annual_savings + future_value_of_initial_savings

    overshoot_amount = future_value - downpayment if future_value > downpayment else 0

    hous_price_at_buying_age = round(hous_price_at_buying_age, 1)
    required_annual_savings = round(required_annual_savings, 1)
    downpayment = round(downpayment, 1)
    annual_savings = round(annual_savings, 1)
    future_value = round(future_value, 1)
    overshoot_amount = round(overshoot_amount, 1)
    return_rate = round(return_rate * 100, 1) 

    print(f"downpayment: {downpayment}")
    print(f"hous price at buying age: {hous_price_at_buying_age}")
    print(f"Wealth atm: {initial_savings}")
    print(f"Age at purchase: {house_purchase_age}")

    # Graph für Haus, Auto, Uhr usw.
    car_price = calculate_car_price(car_type)
    travel_price = calculate_travel_price(travel_type)
    watch_price = calculate_watch_price(watch_type)
    wedding_price = calculate_wedding_price(wedding_type)

    dreams = []

    if hous_price_at_buying_age and house_purchase_age:
        dreams.append({'age': house_purchase_age, 'price': hous_price_at_buying_age, 'label': 'Hauskauf', 'color': 'blue'})

    if car_age and car_price:
        dreams.append({'age': car_age, 'price': car_price, 'label': 'Autokauf', 'color': 'red'})

    if travel_age and travel_price:
        dreams.append({'age': travel_age, 'price': travel_price, 'label': 'Traumreise', 'color': 'red'})

    if watch_age and watch_price:
        dreams.append({'age': watch_age, 'price': watch_price, 'label': 'Traumuhr', 'color': 'red'})

    if wedding_age and wedding_price:
        dreams.append({'age': wedding_age, 'price': wedding_price, 'label': 'Traumhochzeit', 'color': 'red'})

    dream_traces = []
    for dream in dreams:
        trace = go.Scatter(
            x=[dream['age']],
            y=[dream['price']],
            mode='markers+text',
            name=dream['label'],
            text=[f"{dream['label']}: {dream['price']} CHF"],
            textposition='top center',
            marker=dict(
                size=10,
                color=dream['color'],
                symbol='diamond'
            )
        )
        dream_traces.append(trace)

    dream_layout = go.Layout(
        title='Geplante Anschaffungen: Haus, Auto, Uhr usw.',
        xaxis=dict(title='Alter'),
        yaxis=dict(title='Betrag (CHF)'),
        showlegend=True
        )

    fig_dreams = go.Figure(data=dream_traces, layout=dream_layout)
    plot_html_dreams = pio.to_html(fig_dreams, full_html=False)

    print(f"Dreams Liste: {dream_traces}")

    # Suppose find_residual_income() returns a list of tuples: [(age, residual_income), ...]
    ages = [d[0] for d in residual_income_list]
    incomes = [d[1] for d in residual_income_list]

    #car, watch usw
    planned_purchases = [
    {"age": car_age, "value": car_price},  # Buy a car at 40
    {"age": watch_age, "value": watch_price},  # Buy a vacation home at 45
    {"age": wedding_age, "value": wedding_price},
    {"age": travel_age, "value": travel_price}]
    expenditures = {item['age']: item['value'] for item in planned_purchases}

    print(f"expenditures: {expenditures}")

    municipalities = tax_data['Municipality'].dropna().unique().tolist()

    # Separate data for visualization
    years = [entry[0] for entry in final_list]  # Ages
    incomes_after_tax = [entry[1] for entry in final_list]  # Income after tax

    years1 = [entry[0] for entry in total_cost_list]  # Ages
    costs = [entry[1] for entry in total_cost_list]


    # Create Plotly visualization
    trace_income = go.Scatter(x=years, y=incomes_after_tax, mode='lines+markers', name='Income After Tax')
    trace_costs = go.Scatter(x=years1, y=costs, mode='lines+markers', name='Total Costs')
    layout = go.Layout(
        title='Income vs Total Costs Projection',
        xaxis=dict(title='Age'),
        yaxis=dict(title='Amount (CHF)'),
    )
    fig = go.Figure(data=[trace_income, trace_costs], layout=layout)

    # Generate HTML representation of the plot
    plot_html = pio.to_html(fig, full_html=False)

    events = [
        {"name": "Wedding", "type_key": "wedding_type", "age_key": "wedding_age"},
        {"name": "Watch", "type_key": "watch_type", "age_key": "watch_age"},
        {"name": "Travel", "type_key": "travel_type", "age_key": "travel_age"},
        {"name": "Car", "type_key": "car_type", "age_key": "car_age"},
        {"name": "House", "type_key": "hous_price_at_buying_age", "age_key": "house_purchase_age"},
    ]

    current_year = 2024
    timeline_event = []
    for event in events:
        age_key = event["age_key"]
        type_key = event["type_key"]

        # Überprüfen, ob das Alter für das Ereignis in der Session gespeichert ist
        if age_key in session:
            age = session[age_key]
            event_year = current_year + (age - current_age)
            event_name = event["name"]

            # Wenn ein Ereignistyp vorhanden ist, füge ihn zum Ereignisnamen hinzu (z.B. Art der Hochzeit, Auto, etc.)
            if type_key and type_key in session:
                event_name = f"{session[type_key]} {event_name}"

            timeline_event.append({"name": event_name, "age": age, "year": event_year})




    # Render results in the 'results.html' template
    return render_template(
        'results.html',
        projections=final_projections,
        plot_html=plot_html,
        plot_html_dreams=plot_html_dreams,
        municipalities=municipalities,
        hous_price_at_buying_age=hous_price_at_buying_age,
        downpayment=downpayment,
        years_until_downpayment=years_until_downpayment,
        annual_savings=annual_savings,
        future_value=future_value,
        overshoot_amount=overshoot_amount,
        required_annual_savings=required_annual_savings,
        initial_savings=initial_savings,
        retirement_age=retirement_age,
        return_rate=return_rate,
        timeline_event=timeline_event,
        ages=ages,
        incomes=incomes,
        expenditures=expenditures
    )

@app.route('/update_graph', methods=['POST'])
def update_graph():
    # Get the selected municipality from the request
    data = request.get_json()
    selected_location = data.get('location')

    session['location'] = selected_location

    # Example logic to create new plot HTML
    # Replace this with your actual graph generation code
    plot_html = f"<p>Updated graph for {selected_location}</p>"

    return jsonify({'plot_html': plot_html})

@app.route('/download-excel')
def download_excel():
    return send_from_directory(directory='/Users/leorupena/Raiffeisen_Projekt/static', path='General_Project.xlsx', as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True, port=5001)
