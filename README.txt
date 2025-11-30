🛒 Weekly Grocery Shopping Optimizer
Optimize your weekly grocery shopping based on nutrition, cost, and pantry stock.

The Weekly Grocery Shopping Optimizer is an intelligent Streamlit-based application that uses linear programming (PuLP) to generate a cost-efficient and nutritionally balanced shopping list for your household. It accounts for:

👥 Household size, age, gender

🥗 Nutritional needs based on dietary guidelines

📦 Existing pantry stock

💰 Grocery item prices across stores

🌈 Food category diversity

📊 Nutrition + cost optimization

📥 Downloadable Excel shopping lists

This app ensures your weekly grocery plan is cheap, healthy, and personalized.

🚀 Features
👥 Household-Based Nutrition

Add members with age and gender

Automatically pulls nutritional requirements from your dataset

Computes both daily and weekly needs

📦 Stock Awareness

Upload pantry stock to avoid buying duplicates

App automatically subtracts nutrients available from stock

🧠 Optimization Engine

Uses PuLP linear programming to:

Minimize total grocery cost

Meet weekly protein, carb, fat, and calorie requirements

Enforce dietary diversity (protein, grains, veggies, fruits, fats/nuts)

Respect maximum quantity limits for each item

Use integer quantities (whole packages only)

🏪 Store-Separated Outputs

The final shopping list is grouped by stores such as:

Costco

Kroger

Meijer

📤 Excel Output

Generates an Excel file with:

Summary sheet

Full shopping list

Store-specific sheets

