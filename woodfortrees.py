import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import math

st.title("Can't see the wood for the trees?")
st.write("""
This application is designed to create forest plots of data and compare results to a reference to support interpretation of differences between results.  

*Use the ... menu next to the plot (when you mouse over it) to download a copy.*
""")

st.write("---")

# Data editing
st.header("Edit/add data")
st.write("""
You can paste data from a 3 column table in a spreadsheet by clicking on the first cell and using the appropriate keyboard shortcut for your system (<ctrl>-V or <cmd>-V), or paste from the Edit menu.  
""")
data = pd.DataFrame({"Label":["Reference","Test 1", "Test 2"],"Estimate":[0.0,4.0,2.0],"SE":[1.0,1.0,1.0]})
edited_data = st.experimental_data_editor(data,num_rows="dynamic", use_container_width=True)
st.write("---")

# Result plotting
st.header("Forest plot: original data")
st.write("""
This plot will present the datapoints and their 95% confidence intervals. 

*Confidence intervals overlapping the "Null" line do not provide strong evidence against the null hypothesis (of no effect).*
""")
ch1title = st.sidebar.text_input("Chart title", value="Result comparison")
xaxistitle = st.sidebar.text_input("X axis title", value="Estimate")
yaxistitle = st.sidebar.text_input("Y axis title", value="Result")
error_bars = alt.Chart(edited_data, title=ch1title).transform_calculate(
    lowci = "datum.Estimate - 1.96 * datum.SE",
    highci = "datum.Estimate + 1.96 * datum.SE"
).mark_errorbar().encode(
  x = alt.X('lowci:Q',axis=alt.Axis(title=xaxistitle)),
  x2 = 'highci:Q',
  y = alt.Y('Label',axis=alt.Axis(title=yaxistitle))
)
nulldata = pd.DataFrame({'position':[0],'color':['black'],'label':["Null"]})
nullline = alt.Chart(nulldata).mark_rule().encode(
      x='position:Q',
      color=alt.Color('color:N', scale=None)
    )
nulltextoffset = -(len(edited_data)*10+10)
nulltext = alt.Chart(nulldata).mark_text(align='center', yOffset=nulltextoffset, angle=0
    ).encode(
        x='position:Q',
        text='label',
    )
points = alt.Chart(edited_data).mark_point(filled=True, color='black').encode(
  x = 'Estimate:Q',
  y = 'Label',
)
forestplot = error_bars + nullline + nulltext + points
st.altair_chart(forestplot, use_container_width=True)
st.write("---")

# Comparison to reference
st.header("Comparison to reference")
st.write("""
This plot will present the difference between test datapoints and a reference (control) datapoint, showing the 95% confidence intervals of the difference between each datapoint and the reference. 

*Confidence intervals overlapping the "Null" line do not provide strong evidence against the null hypothesis (of no difference between this datapoint and control).*
""")
reference = st.selectbox("Select reference", edited_data["Label"])

comparison_data = edited_data.copy()
reference_Estimate = float(comparison_data[comparison_data['Label'] == reference]['Estimate'])
reference_SE = float(comparison_data[comparison_data['Label'] == reference]['SE'])
comparison_data['diff'] = comparison_data['Estimate'] - reference_Estimate
comparison_data['diff_SE'] = comparison_data['SE'].apply(lambda x: math.sqrt(x**2 + reference_SE**2))
comparison_data = comparison_data.drop(comparison_data.index[comparison_data['Label'] == reference].tolist())
comparison_data['low_CI'] = comparison_data['diff'] - 1.95*comparison_data['diff_SE']
comparison_data['high_CI'] = comparison_data['diff'] + 1.95*comparison_data['diff_SE']

error_bars_comparison = alt.Chart(comparison_data, title=f"Comparison to reference ({reference})").transform_calculate(
    lowci = "datum.diff - 1.96 * datum.diff_SE",
    highci = "datum.diff + 1.96 * datum.diff_SE"
).mark_errorbar().encode(
  x = alt.X('lowci:Q',axis=alt.Axis(title=xaxistitle)),
  x2 = 'highci:Q',
  y = alt.Y('Label',axis=alt.Axis(title=yaxistitle))
)
points_comparison = alt.Chart(comparison_data).mark_point(filled=True, color='black').encode(
  x = 'diff:Q',
  y = 'Label',
)
refdata = pd.DataFrame({'position':[0],'color':['black'],'label':["Reference"]})
refline = alt.Chart(refdata).mark_rule().encode(
      x='position:Q',
      color=alt.Color('color:N', scale=None)
    )
reftextoffset = -(len(edited_data)*10+10)
reftext = alt.Chart(refdata).mark_text(align='center', yOffset=reftextoffset, angle=0
    ).encode(
        x='position:Q',
        text='label',
    )
forestplot = error_bars_comparison + refline + reftext + points_comparison
st.altair_chart(forestplot, use_container_width=True)
st.dataframe(comparison_data[['diff','diff_SE','low_CI','high_CI']], use_container_width=True)
