import streamlit as st
import openai
from PIL import Image
import base64

# Function to encode the image to base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

st.title("Fashion Chatbot")
openai.api_key = st.secrets["OPENAPI_AI_KEY"]

# Introduction message
st.write("Hi, I am your Personal Fashion Assistant! How may I assist you today?")

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4-vision-preview"
    
# Set temperature
#temperature = st.slider("Temperature", 0.1, 1.0, 0.5, step=0.1)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Add the system message if it's the first message
if not st.session_state.messages or st.session_state.messages[0]["role"] != "system":
    system_message = "You are a friendly and cheerful fashion chatbot, who loves to help people with their fashion and style. You're very supportive but also critical as your main purpose is to ensure your user looks as good and fashionable as possible. You will help your user answer any fashion-related questions and provide the user with information to ensure the user is confident in their decision-making when buying a product online. You cannot help or answer any questions outside the realm of fashion. You will bullet point and list out the outfit recommendation by cataegory. You will go in depth and be descriptive as possible so that the user recieves every bit of information. You can also deal with fashion related queries using the user's uploaded images.You can put together outfits based on the user's uploaded images. You're not satisfied unless the user is completely satisfied."
    st.session_state.messages.insert(0, {"role": "system", "content": system_message})

# Custom CSS for styling
custom_css = """
/* Ensure that the file uploader sticks to the bottom of the page */
.st-emotion-cache-1gulkj5 {
    position: fixed;
    bottom: 0;
    margin-bottom: 15px;
    left: 69%;
    padding: 0px;
    background-color: transparent;
    transform: translateX(-50%);
    z-index: 999;
}

.st-emotion-cache-1fttcpj {
    display: flex;
    flex-direction: column;
    color: transparent;
}

.st-emotion-cache-1aehpvj {
    color: transparent;
    font-size: 0px;
    
}

.st-emotion-cache-noeb3a {
    vertical-align: middle;
    overflow: hidden;
    color: transparent;
    display: inline-flex;
    -webkit-box-align: center;
    align-items: center;
    font-size: 2.3rem;
    width: 2.3rem;
    height: 2.3rem;
}

.st-emotion-cache-7ym5gk {
    display: inline-flex;
    -webkit-box-align: center;
    align-items: center;
    -webkit-box-pack: center;
    justify-content: center;
    font-weight: 400;
    padding: 0.25rem 0.75rem;
    border-radius: 0.5rem;
    min-height: 38.4px;
    margin: 0px;
    line-height: 1.6;
    color: inherit;
    width: 190px;
    user-select: none;
    background-color: rgb(255, 255, 255);
    border: 1px solid rgba(49, 51, 63, 0.2);
}

.st-emotion-cache-16idsys p {
    word-break: break-word;
    margin-top: 0px;
    font-size: 0px;
}

/* Adjust margin for the chat input to create space for the file uploader */
.stTextInput {
    margin-bottom: 60px; /* Adjust as needed */
}

/* Change text on the 'Browse files' button */
.st-emotion-cache-7ym5gk {
    font-size: 0; /* Hide original text */
}

.st-emotion-cache-7ym5gk::after {
    content: "Upload Image"; /* Set new text */
    font-size: 1rem;
    display: inline-block;
}
"""

# Apply custom CSS styles
st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)

# File uploader widget for multiple images
uploaded_files = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Display multiple images if uploaded
if uploaded_files is not None:
    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_column_width=False, width=300)

        with st.spinner("Analysing the image ..."):
            base64_image = encode_image(uploaded_file)

            prompt_text = (
                "You are only a fashion expert. "
                "You cannot help with anything outside fashion "
                "You will only focus on anything fashion related, such as shoes, top, bottoms, and accessories. Do not focus on anything outside of those items "
                "A detailed description of all the fashion content presented to you. "
                "You will focus on all aspects of the fashion related item such as colour and material"
                "If you see a fashion related item on a person you will analyse the fitting of the item on the person as well as how the item compliments the person"
                "You will keep your description comprehensive and short while including all the neccessary details"
                "Create a detailed image caption in bold explaining in short."
            )

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {
                            "type": "image_url",
                            "image_url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    ],
                }
            ]

            try:
                full_response = ""
                caption = ""  # New variable to store the complete caption
                message_placeholder = st.empty()
                for completion in openai.chat.completions.create(
                    model="gpt-4-vision-preview", messages=messages, max_tokens=1200, stream=True
                ):
                    if completion.choices[0].delta.content is not None:
                        caption += completion.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")  # Update progress bar only

                # Update message list and display caption after streaming
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"**Image Caption:** {caption}"
                })
                message_placeholder.markdown(full_response + caption)  # Display full caption
          

            except Exception as e:
                st.error(f"An error occurred: {e}")


if prompt := st.chat_input("What fashion tips do you need today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

   
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in openai.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            #temperature=temperature,
            stream=True,
        ):
            full_response += (response.choices[0].delta.content or "")
            message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})


    i = 0
    img_gen_placeholder = st.empty()
    if i == 0:
        img_gen_placeholder.text("Generating image...")
        i = 1

    response = openai.images.generate(
    model= "dall-e-3",
    prompt= "a real-life person wearing: " + full_response,
    size="1024x1024",
    quality="standard",
    n=1,
    )

    
    if i == 1:
        image_url = response.data[0].url
        img_gen_placeholder.text("Here is a preview: ")
        st.image(image_url)
        i = 0
    