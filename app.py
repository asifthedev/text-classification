import transformers
import streamlit as st

@st.cache_resource
def load_model():
    with st.spinner("Downloading model..."):
        return transformers.pipeline("text-classification")
st.title(":red[Text] Classification")
input = st.text_input("Enter your text")

if st.button("Classify"):
    classify = load_model()
    result = classify(input)
    st.metric("Label", result[0]['label'])