import streamlit as st
import pandas as pd
from pulp import LpMinimize, LpProblem, LpVariable, lpSum, LpStatus
import io

# Page configuration
st.set_page_config(
    page_title="Weekly Grocery Optimizer",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 Weekly Grocery Shopping Optimizer")
st.markdown("### Optimize your grocery shopping based on nutritional needs and budget")

# Initialize session state
if 'household_members' not in st.session_state:
    st.session_state.household_members = []
if 'cost_df' not in st.session_state:
    st.session_state.cost_df = None
if 'nutrition_df' not in st.session_state:
    st.session_state.nutrition_df = None
if 'check_df' not in st.session_state:
    st.session_state.check_df = None
if 'stock_df' not in st.session_state:
    st.session_state.stock_df = None

# Function to load default data
def load_default_grocery_data():
    """Load default grocery data from Data/Grocery.xlsx"""
    try:
        st.session_state.cost_df = pd.read_excel("Data/Grocery.xlsx", sheet_name="Cost_List")
        st.session_state.nutrition_df = pd.read_excel("Data/Grocery.xlsx", sheet_name="Nutrition_List")
        st.session_state.check_df = pd.read_excel("Data/Grocery.xlsx", sheet_name="Check_Nutrition")
        return True
    except Exception as e:
        st.error(f"Error loading default grocery data: {str(e)}")
        return False

def load_default_stock_data():
    """Load default stock data from Stock.xlsx"""
    try:
        st.session_state.stock_df = pd.read_excel("Data/Stock.xlsx")
        return True
    except Exception as e:
        st.error(f"Error loading default stock data: {str(e)}")
        return False

# Load default data on first run
if st.session_state.cost_df is None:
    load_default_grocery_data()
if st.session_state.stock_df is None:
    load_default_stock_data()

# Sidebar for data upload
with st.sidebar:
    st.header("📁 Data Management")
    
    # Grocery Data Section
    st.subheader("🥗 Grocery Database")
    
    if st.session_state.cost_df is not None:
        st.success("✅ Using default grocery data")
        st.write(f"- Food items: {len(st.session_state.cost_df)}")
    
    with st.expander("📤 Upload Custom Grocery Data"):
        st.markdown("Upload a custom Excel file with sheets: `Cost_List`, `Nutrition_List`, `Check_Nutrition`")
        
        # Download default grocery database
        try:
            # Create download for default grocery data
            output_grocery = io.BytesIO()
            with pd.ExcelWriter(output_grocery, engine='openpyxl') as writer:
                if st.session_state.cost_df is not None:
                    st.session_state.cost_df.to_excel(writer, sheet_name='Cost_List', index=False)
                if st.session_state.nutrition_df is not None:
                    st.session_state.nutrition_df.to_excel(writer, sheet_name='Nutrition_List', index=False)
                if st.session_state.check_df is not None:
                    st.session_state.check_df.to_excel(writer, sheet_name='Check_Nutrition', index=False)
            
            st.download_button(
                label="📥 Download Default Grocery Database",
                data=output_grocery.getvalue(),
                file_name="grocery_database.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Download the default grocery database as a template"
            )
        except:
            pass
        
        uploaded_grocery_file = st.file_uploader(
            "Upload Grocery Excel File",
            type=['xlsx'],
            key="grocery_uploader",
            help="Excel file with Cost_List, Nutrition_List, and Check_Nutrition sheets"
        )
        
        if uploaded_grocery_file is not None:
            try:
                st.session_state.cost_df = pd.read_excel(uploaded_grocery_file, sheet_name="Cost_List")
                st.session_state.nutrition_df = pd.read_excel(uploaded_grocery_file, sheet_name="Nutrition_List")
                st.session_state.check_df = pd.read_excel(uploaded_grocery_file, sheet_name="Check_Nutrition")
                st.success("✅ Custom grocery data loaded!")
                st.write(f"- Food items: {len(st.session_state.cost_df)}")
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
        
        if st.button("🔄 Reset to Default Grocery Data"):
            load_default_grocery_data()
            st.rerun()
    
    st.divider()
    
    # Stock Data Section
    st.subheader("📦 Stock Inventory")
    
    if st.session_state.stock_df is not None:
        stock_count = len(st.session_state.stock_df[st.session_state.stock_df['Quantity_in_Stock_lb'] > 0])
        st.success(f"✅ Stock loaded ({stock_count} items)")
    
    # Download stock template
    try:
        stock_template = pd.read_excel("Data/Stock.xlsx")
        output_template = io.BytesIO()
        with pd.ExcelWriter(output_template, engine='openpyxl') as writer:
            stock_template.to_excel(writer, sheet_name='Stock', index=False)
        
        st.download_button(
            label="📥 Download Stock Template",
            data=output_template.getvalue(),
            file_name="stock_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Download template to fill in your current stock"
        )
    except:
        pass
    
    with st.expander("📤 Upload Your Stock"):
        st.markdown("Upload your current stock inventory")
        
        uploaded_stock_file = st.file_uploader(
            "Upload Stock Excel File",
            type=['xlsx'],
            key="stock_uploader",
            help="Excel file with your current stock inventory"
        )
        
        if uploaded_stock_file is not None:
            try:
                st.session_state.stock_df = pd.read_excel(uploaded_stock_file)
                st.success("✅ Custom stock data loaded!")
                stock_count = len(st.session_state.stock_df[st.session_state.stock_df['Quantity_in_Stock_lb'] > 0])
                st.write(f"- Items in stock: {stock_count}")
            except Exception as e:
                st.error(f"Error loading stock file: {str(e)}")
        
        if st.button("🔄 Reset to Default Stock"):
            load_default_stock_data()
            st.rerun()

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["👥 Household Members", "📊 Current Stock", "🎯 Generate Shopping List", "ℹ️ About"])

# Tab 1: Household Members
with tab1:
    st.header("Add Household Members")
    
    col1, col2 = st.columns(2)
    
    with col1:
        member_age = st.number_input("Age", min_value=1, max_value=120, value=25)
    
    with col2:
        member_gender = st.selectbox("Gender", ["male", "female"])
    
    if st.button("➕ Add Member"):
        st.session_state.household_members.append({
            'age': member_age,
            'gender': member_gender
        })
        st.success(f"Added {member_gender}, age {member_age}")
    
    # Display current household members
    if st.session_state.household_members:
        st.subheader("Current Household Members")
        
        members_data = []
        for idx, member in enumerate(st.session_state.household_members):
            members_data.append({
                'Member #': idx + 1,
                'Age': member['age'],
                'Gender': member['gender'].capitalize()
            })
        
        members_df = pd.DataFrame(members_data)
        st.dataframe(members_df, use_container_width=True)
        
        # Clear all members button
        if st.button("🗑️ Clear All Members"):
            st.session_state.household_members = []
            st.rerun()
        
        # Calculate total nutritional requirements
        if st.session_state.check_df is not None:
            st.subheader("Daily Nutritional Requirements")
            
            total_requirements = {
                "Calories": 0,
                "Protein (g)": 0,
                "Carbohydrates (g)": 0,
                "Fat (g)": 0
            }
            
            for member in st.session_state.household_members:
                row = st.session_state.check_df[
                    (st.session_state.check_df["Age_Sex_Group"].str.lower() == member['gender'])
                    & (st.session_state.check_df["Min_Age"] <= member['age'])
                    & (st.session_state.check_df["Max_Age"] >= member['age'])
                ]
                
                if not row.empty:
                    total_requirements["Calories"] += row["Min_Calorie"].values[0]
                    total_requirements["Protein (g)"] += row["min_Protein"].values[0]
                    total_requirements["Carbohydrates (g)"] += row["min_Carbohydrate"].values[0]
                    total_requirements["Fat (g)"] += row["min_Fat"].values[0]
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Daily Calories", f"{total_requirements['Calories']:.0f}")
            col2.metric("Daily Protein", f"{total_requirements['Protein (g)']:.0f}g")
            col3.metric("Daily Carbs", f"{total_requirements['Carbohydrates (g)']:.0f}g")
            col4.metric("Daily Fat", f"{total_requirements['Fat (g)']:.0f}g")
            
            st.info(f"**Weekly Requirements:** {total_requirements['Calories']*7:.0f} cal | "
                   f"{total_requirements['Protein (g)']*7:.0f}g protein | "
                   f"{total_requirements['Carbohydrates (g)']*7:.0f}g carbs | "
                   f"{total_requirements['Fat (g)']*7:.0f}g fat")

# Tab 2: Current Stock
with tab2:
    st.header("Current Stock Inventory")
    
    if st.session_state.stock_df is not None:
        stock_display = st.session_state.stock_df[
            st.session_state.stock_df['Quantity_in_Stock_lb'] > 0
        ].copy()
        
        if not stock_display.empty:
            st.dataframe(stock_display, use_container_width=True)
            st.info(f"Total items in stock: {len(stock_display)}")
        else:
            st.warning("No items currently in stock")
    else:
        st.warning("Please upload the grocery list file to view stock")

# Tab 3: Generate Shopping List
with tab3:
    st.header("Generate Optimized Shopping List")
    
    if not st.session_state.household_members:
        st.warning("⚠️ Please add household members first")
    elif st.session_state.cost_df is None:
        st.warning("⚠️ Please upload the grocery list file")
    else:
        if st.button("🚀 Generate Shopping List", type="primary"):
            with st.spinner("Optimizing your shopping list..."):
                try:
                    # Calculate nutritional requirements
                    required_nutrients = {
                        "Min_Calorie": 0,
                        "Min_Protein": 0,
                        "Min_Carbohydrate": 0,
                        "Min_Fat": 0
                    }
                    
                    for member in st.session_state.household_members:
                        row = st.session_state.check_df[
                            (st.session_state.check_df["Age_Sex_Group"].str.lower() == member['gender'])
                            & (st.session_state.check_df["Min_Age"] <= member['age'])
                            & (st.session_state.check_df["Max_Age"] >= member['age'])
                        ]
                        
                        if not row.empty:
                            required_nutrients["Min_Calorie"] += row["Min_Calorie"].values[0]
                            required_nutrients["Min_Protein"] += row["min_Protein"].values[0]
                            required_nutrients["Min_Carbohydrate"] += row["min_Carbohydrate"].values[0]
                            required_nutrients["Min_Fat"] += row["min_Fat"].values[0]
                    
                    # Merge data
                    data = pd.merge(st.session_state.cost_df, st.session_state.nutrition_df, on="Food")
                    data = pd.merge(data, st.session_state.stock_df, on="Package Description", how="left").fillna(0)
                    data['lb'] = data['lb'].astype(float)
                    
                    # Create optimization model
                    model = LpProblem("Weekly_Shopping_Optimization", LpMinimize)
                    
                    # Decision variables
                    buy_qty = {
                        row["Package Description"]: LpVariable(
                            name=row["Package Description"].replace(" ", "_").replace(",", "").replace("(", "").replace(")", ""),
                            lowBound=0,
                            upBound=row["Max_quantity"],
                            cat="Integer"
                        )
                        for _, row in data.iterrows()
                    }
                    
                    # Objective: minimize cost
                    model += lpSum(data.loc[i, "price"] * buy_qty[data.loc[i, "Package Description"]] 
                                  for i in range(len(data)))
                    
                    # Nutritional constraints
                    for nutrient, col in [("Min_Protein", "Protein (g)"), 
                                         ("Min_Carbohydrate", "Carbs (g)"),
                                         ("Min_Fat", "Fat (g)"),
                                         ("Min_Calorie", "kcal")]:
                        model += (
                            lpSum(
                                data.loc[i, col] * buy_qty[data.loc[i, "Package Description"]]
                                for i in range(len(data))
                            )
                            + 
                            sum(
                                data.loc[i, col] * data.loc[i, "Quantity_in_Stock_lb"]
                                for i in range(len(data))
                            )
                            >= required_nutrients[nutrient] * 7,
                            f"{nutrient}_requirement"
                        )

                    
                    # Food basket diversity constraints
                    basket_categories = [
                        "Protein",
                        "Grains & Carbohydrate Sources",
                        "Vegetables",
                        "Fruits",
                        "Fats, Nuts & Seeds"
                    ]
                    
                    has_cat = {cat: LpVariable(f"Has_{cat.replace(' ', '_').replace(',', '').replace('&', 'and')}", 
                                              cat="Binary") for cat in basket_categories}
                    
                    for cat in basket_categories:
                        cat_items = data[data["Food Basket"] == cat].index.tolist()
                        if len(cat_items) > 0:
                            model += (
                                lpSum(buy_qty[data.loc[i, "Package Description"]] for i in cat_items)
                                #+ lpSum((data.loc[i, "Quantity_in_Stock_lb"] > 0) * 1 for i in cat_items)
                                + lpSum(1 for i in cat_items if data.loc[i, "Quantity_in_Stock_lb"] > 0)
                                >= has_cat[cat],
                                f"{cat}_presence"
                            )
                            #model += (has_cat[cat] == 1, f"Must_have_{cat}")
                            model += has_cat[cat] <= 1
                    
                    # Solve
                    status = model.solve()
                    
                    if LpStatus[status] == "Optimal":
                        st.success("✅ Optimization Complete!")
                        
                        # Collect results
                        results = []
                        for food in buy_qty:
                            qty = buy_qty[food].value()
                            if qty and qty > 0:
                                qty = int(round(qty))
                                row_data = data.loc[data["Package Description"] == food].iloc[0]
                                cost = row_data["price"] * qty
                                total_weight = row_data["lb"] * qty
                                results.append({
                                    "Store": row_data["Store"],
                                    "Food": row_data["Food"],
                                    "Package Description": food,
                                    "lb_per_package": row_data["lb"],
                                    "price_per_package": row_data["price"],
                                    "Qty_to_Buy": qty,
                                    "Total_Weight_lb": round(total_weight, 2),
                                    "Weekly_Cost": round(cost, 2)
                                })
                        
                        results_df = pd.DataFrame(results)
                        
                        total_cost = results_df["Weekly_Cost"].sum()
                        total_items = results_df["Qty_to_Buy"].sum()
                        total_weight = results_df["Total_Weight_lb"].sum()
                        
                        # Display summary metrics
                        st.subheader("Your Optimized Shopping List")
                        
                        metric_col1, metric_col2, metric_col3 = st.columns(3)
                        metric_col1.metric("Total Weekly Cost", f"${total_cost:.2f}")
                        metric_col2.metric("Total Packages", f"{total_items}")
                        metric_col3.metric("Total Weight", f"{total_weight:.1f} lbs")
                        
                        # Display full table
                        st.dataframe(
                            results_df.style.format({
                                "lb_per_package": "{:.2f}",
                                "price_per_package": "${:.2f}",
                                "Total_Weight_lb": "{:.2f}",
                                "Weekly_Cost": "${:.2f}"
                            }),
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        st.divider()
                        
                        # Group by store
                        st.subheader("Shopping List by Store")
                        for store in sorted(results_df["Store"].unique()):
                            with st.expander(f"🏪 {store}", expanded=True):
                                store_items = results_df[results_df["Store"] == store].copy()
                                store_cost = store_items['Weekly_Cost'].sum()
                                store_packages = store_items['Qty_to_Buy'].sum()
                                
                                st.write(f"**{store_packages} packages | ${store_cost:.2f}**")
                                
                                # Display store-specific items
                                st.dataframe(
                                    store_items[["Food", "Package Description", "lb_per_package", 
                                               "price_per_package", "Qty_to_Buy", "Total_Weight_lb", "Weekly_Cost"]].style.format({
                                        "lb_per_package": "{:.2f}",
                                        "price_per_package": "${:.2f}",
                                        "Total_Weight_lb": "{:.2f}",
                                        "Weekly_Cost": "${:.2f}"
                                    }),
                                    use_container_width=True,
                                    hide_index=True
                                )
                        
                        st.divider()
                        
                        # Download button
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            # Summary sheet
                            summary_data = {
                                'Metric': ['Total Cost', 'Total Packages', 'Total Weight (lbs)', 'Number of Stores'],
                                'Value': [f'${total_cost:.2f}', total_items, f'{total_weight:.1f}', len(results_df["Store"].unique())]
                            }
                            summary_df = pd.DataFrame(summary_data)
                            summary_df.to_excel(writer, sheet_name='Summary', index=False)
                            
                            # Full shopping list
                            results_df.to_excel(writer, sheet_name='Shopping List', index=False)
                            
                            # By store sheets
                            for store in sorted(results_df["Store"].unique()):
                                store_items = results_df[results_df["Store"] == store]
                                store_items.to_excel(writer, sheet_name=store[:31], index=False)  # Excel sheet name limit
                        
                        st.download_button(
                            label="📥 Download Shopping List (Excel)",
                            data=output.getvalue(),
                            file_name="weekly_shopping_list.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:
                        st.error(f"Optimization failed with status: {LpStatus[status]}")
                        
                except Exception as e:
                    st.error(f"Error during optimization: {str(e)}")
                    st.exception(e)

# Tab 4: About
with tab4:
    st.header("ℹ️ About Weekly Grocery Optimizer")
    
    # Introduction
    st.markdown("""
    ### 🎯 What is this app?
    
    The **Weekly Grocery Optimizer** is an intelligent shopping assistant that helps you:
    - 🥗 Meet your household's nutritional requirements
    - 💰 Minimize your grocery spending
    - 🛒 Plan efficient shopping trips
    - 📊 Track your pantry inventory
    - 🌈 Ensure dietary diversity
    """)
    
    st.divider()
    
    # How it works
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🔧 How It Works
        
        **1. Input Your Household**
        - Add family members with their age and gender
        - The app automatically calculates nutritional needs based on dietary guidelines
        
        **2. Update Your Stock**
        - Download the stock template
        - Fill in what you already have at home
        - Upload to avoid buying duplicates
        
        **3. Generate Your List**
        - Click "Generate Shopping List"
        - Our optimization algorithm finds the best combination
        - Get a cost-minimized, nutrition-optimized shopping list
        """)
    
    with col2:
        st.markdown("""
        ### 🧮 The Science Behind It
        
        **Linear Programming Optimization**
        - Uses the PuLP library for mathematical optimization
        - Minimizes total cost while meeting constraints
        
        **Nutritional Constraints**
        - Meets minimum weekly requirements for:
          - Calories
          - Protein
          - Carbohydrates
          - Fat
        
        **Diversity Constraints**
        - Ensures variety across food categories:
          - Proteins
          - Grains & Carbs
          - Vegetables
          - Fruits
          - Fats, Nuts & Seeds
        """)
    
    st.divider()
    
    # Key Features
    st.markdown("""
    ### ✨ Key Features
    """)
    
    feature_col1, feature_col2, feature_col3 = st.columns(3)
    
    with feature_col1:
        st.markdown("""
        **📊 Smart Planning**
        - Age and gender-specific nutrition
        - Weekly meal planning
        - Stock-aware recommendations
        """)
    
    with feature_col2:
        st.markdown("""
        **💰 Cost Optimization**
        - Finds cheapest combination
        - Compares across stores
        - Maximizes budget efficiency
        """)
    
    with feature_col3:
        st.markdown("""
        **🎨 User Friendly**
        - Intuitive interface
        - Downloadable shopping lists
        - Customizable databases
        """)
    
    st.divider()
    
    # Getting Started
    st.markdown("""
    ### 🚀 Getting Started
    
    **Quick Start Guide:**
    
    1. **👥 Add Household Members**
       - Navigate to "Household Members" tab
       - Enter age and gender for each person
       - View calculated nutritional requirements
    
    2. **📦 Update Stock (Optional)**
       - Go to "Current Stock" tab
       - Download the stock template
       - Fill in your current inventory
       - Upload back to the app
    
    3. **🛒 Generate Your List**
       - Click on "Generate Shopping List" tab
       - Press the "Generate Shopping List" button
       - Review your optimized shopping plan
       - Download as Excel file for shopping
    
    4. **🏪 Shop Smart**
       - Items are organized by store
       - Follow the quantities recommended
       - Enjoy cost savings and balanced nutrition!
    """)
    
    st.divider()
    
    # Data Sources
    st.markdown("""
    ### 📚 Data Sources & Customization
    
    **Default Database:**
    - Includes 90+ food items from Costco, Kroger, and Meijer
    - Nutritional data from USDA standards
    - Age/gender-specific requirements based on dietary guidelines
    
    **Customize Your Database:**
    - Download default grocery database from the sidebar
    - Add your own items, stores, and prices
    - Upload your customized version
    - The app adapts to your data!
    """)
    
    st.divider()
    
    # Technical Details
    with st.expander("🔬 Technical Details"):
        st.markdown("""
        **Technologies Used:**
        - **Streamlit**: Web interface
        - **PuLP**: Linear programming optimization
        - **Pandas**: Data manipulation
        - **OpenPyXL**: Excel file handling
        
        **Optimization Model:**
        ```
        Minimize: Total Cost
        
        Subject to:
        - Weekly Protein ≥ Required Protein × 7
        - Weekly Carbs ≥ Required Carbs × 7
        - Weekly Fat ≥ Required Fat × 7
        - Weekly Calories ≥ Required Calories × 7
        - At least one item from each food category
        - Quantity ≤ Max quantity per item
        - Quantity must be integer (whole packages)
        ```
        
        **Constraints:**
        - Maximum quantities per item (to ensure variety)
        - Food basket diversity (protein, grains, vegetables, fruits, fats/nuts)
        - Stock consideration (accounts for what you have)
        - Integer variables (can't buy half packages)
        """)
    
    # FAQ
    with st.expander("❓ Frequently Asked Questions"):
        st.markdown("""
        **Q: Why do I need to add household members?**  
        A: Different ages and genders have different nutritional needs. The app uses this to calculate accurate requirements.
        
        **Q: Can I shop at different stores?**  
        A: Yes! The app shows which items to buy from each store to minimize your total cost.
        
        **Q: What if I don't like a recommended item?**  
        A: You can edit the grocery database to remove items or adjust their availability limits.
        
        **Q: How accurate are the nutritional requirements?**  
        A: Based on USDA dietary guidelines. Consult a nutritionist for specific dietary needs.
        
        **Q: Can I use this for special diets?**  
        A: You can customize the database to include only items that fit your dietary restrictions.
        
        **Q: Why is the optimization taking long?**  
        A: Complex optimizations with many items and constraints can take 10-30 seconds. This is normal.
        
        **Q: What happens if no solution is found?**  
        A: This means constraints are too strict. Try reducing household members or checking your data.
        """)
    
    st.divider()
    
    # Version and Credits
    st.markdown("""
    ### 📝 Version Information
    
    **Version:** 1.0  
    **Last Updated:** November 2024
    
    **Developed with:**
    - Python 3.10+
    - Streamlit
    - PuLP Optimization Library
    
    ---
    
    💡 **Tips for Best Results:**
    - Update your stock regularly for accurate recommendations
    - Review and adjust max quantities in the database
    - Compare generated lists over time to track savings
    - Keep the grocery database updated with current prices
    """)

# Footer
st.markdown("---")
st.markdown("*Grocery Optimizer v1.0 - Helping you shop smarter and healthier*")