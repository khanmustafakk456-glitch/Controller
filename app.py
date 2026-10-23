
import streamlit as st
import main as controller


# Page settings
st.set_page_config(
    page_title="Controller",
    page_icon="🎙️",
    layout="centered"
)


# UI styling
st.markdown(
    """
    <style>
    .block-container {
        max-width: 750px;
        padding-top: 3rem;
    }

    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 700;
    }

    .sub-title {
        text-align: center;
        color: gray;
        font-size: 17px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Header
st.markdown(
    '<div class="main-title">🎙️ Controller</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">Your Voice-Controlled Desktop Assistant</div>',
    unsafe_allow_html=True
)

st.divider()


# Command processing function
def process_command(command):
    if not command:
        st.warning("Please enter or speak a command.")
        return

    st.write("**Command:**", command)

    cleaned_command = controller.clean_command(command)

    controller.open_item(cleaned_command)

    st.success("Command sent to Controller!")


# Voice command section
st.subheader("🎤 Voice Command")

st.write(
    "Click the button and speak your command. "
    "For example: Open Downloads or Screen Off."
)

if st.button("🎙️ Start Listening", use_container_width=True):
    with st.spinner("Listening... Speak now"):
        spoken_text = controller.listen()

    if spoken_text:
        st.write("**Recognized:**", spoken_text)

        cleaned_command = controller.clean_command(spoken_text)

        with st.spinner("Executing command..."):
            controller.open_item(cleaned_command)

        st.success("Command sent to Controller!")

    else:
        st.warning("No command recognized. Please try again.")


st.divider()


# Text command section
st.subheader("⌨️ Type a Command")

with st.form("command_form"):
    user_command = st.text_input(
        "Enter your command",
        placeholder="e.g. Open This PC, Connect Wi-Fi, Screen Off"
    )

    submitted = st.form_submit_button(
        "Run Command",
        use_container_width=True
    )

    if submitted:
        process_command(user_command)


st.divider()


# Available commands
with st.expander("📋 Available Commands"):
    st.markdown(
        """
        **Desktop**
        - Open Desktop files and folders
        - Open This PC
        - Open C Drive
        - Open Downloads
        - Open Documents

        **Windows**
        - Open Control Panel
        - Open Network
        - Open Recycle Bin

        **Applications**
        - Open Wondershare Filmora
        - Open iTunes

        **System**
        - Connect Wi-Fi
        - Screen Off
        """
    )


st.caption("Controller • Voice Assistant")
