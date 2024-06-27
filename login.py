import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from streamlit_float import float_css_helper

# Creating a login widget
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)



def main():
    name, authentication_status, username = authenticator.login('main')
    register_new_user()
    #button1 = st.button('Register new user')
    #if button1:
        #register_new_user()
    if authentication_status:
        update_user_config_file()
        # User is authenticated, show the app content
        st.header("EMA - Emergency Medicine Assistant 🤖🩺")
        
        with st.sidebar:
            st.title("Top Section")
            container = st.container()
            container.float(float_css_helper(bottom="10px"))
            with container:
                authenticate_user()
        
        import time
        
        if st.button('Three cheers', type='primary'):
            st.toast('Hip!')
            time.sleep(.5)
            st.toast('Hip!')
            time.sleep(.5)
            st.toast('Hooray!', icon='🎉')
    
    elif authentication_status is False:
        # Authentication failed
        st.error('Username/password is incorrect')
    
    else:
        # Authentication status is None, show login form
        st.warning('Please enter your username and password')



# Authenticating users
def authenticate_user():
    
    if st.session_state["authentication_status"]:
        #st.markdown("<h1 style='margin-top: -60px;text-align: center;'>EMA 🤖</h1>", unsafe_allow_html=True)
        col1, col2 = st.columns([2,1])
        with col1:
            st.write(f'Welcome *{st.session_state["name"]}*')
        with col2:
            authenticator.logout()
            #if authenticator.logout():
                #update_user_config_file()
    elif st.session_state["authentication_status"] is False:
        st.error('Username/password is incorrect')
    elif st.session_state["authentication_status"] is None:
        st.warning('Please enter your username and password')



# Creating a reset password widget
def reset_password():
    if st.session_state["authentication_status"]:
        try:
            if authenticator.reset_password(st.session_state["username"]):
                st.success('Password modified successfully')
        except Exception as e:
            st.error(e)

# register new user
def register_new_user():
    try:
        email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user(pre_authorization=False)
        if email_of_registered_user:
            st.success('User registered successfully')
            update_user_config_file()
    except Exception as e:
        st.error(e)


#forgot password
def forgot_password():
    try:
        username_of_forgotten_password, email_of_forgotten_password, new_random_password = authenticator.forgot_password()
        if username_of_forgotten_password:
            st.success('New password to be sent securely')
            # The developer should securely transfer the new password to the user.
        elif username_of_forgotten_password == False:
            st.error('Username not found')
    except Exception as e:
        st.error(e)

# Creating a forgot username widget
def forgot_username():
    try:
        username_of_forgotten_username, email_of_forgotten_username = authenticator.forgot_username()
        if username_of_forgotten_username:
            st.success('Username to be sent securely')
            # The developer should securely transfer the username to the user.
        elif username_of_forgotten_username == False:
            st.error('Email not found')
    except Exception as e:
        st.error(e)

# Creating an update user details widget
def update_user_details():
    if st.session_state["authentication_status"]:
        try:
            if authenticator.update_user_details(st.session_state["username"]):
                st.success('Entries updated successfully')
        except Exception as e:
            st.error(e)

    
# Updating the configuration file
def update_user_config_file():
    with open('config.yaml', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)


#authenticator.login('main')
if __name__ == '__main__':
    main()

    update_user_config_file()
