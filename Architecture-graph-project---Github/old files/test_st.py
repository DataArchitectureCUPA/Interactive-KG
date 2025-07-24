
import streamlit as st
import sys

st.write("Hello, Streamlit!")

st.write(f"Python version: {sys.version}")
st.write(f"Streamlit version: {st.__version__}")

if st.button("Click me!"):
    st.write("Button was clicked!")

st.error("If you can see this, Streamlit is working but displaying as an error.")