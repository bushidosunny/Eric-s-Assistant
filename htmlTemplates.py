css = '''
<style>
.chat-message {
    padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex
}
.chat-message.user {
    background-color: #2b313e
}
.chat-message.bot {
    background-color: #475063
}
.chat-message .message {
  width: 80%;
  padding: 0 1.5rem;
  color: #fff;
}
[data-testid="stSidebar"]{
  min-width: 200px;
  max-width: 800px;
}
</style>
'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://mir-s3-cdn-cf.behance.net/project_modules/max_1200/f1a84856240191.59a64e6d80c00.jpg"> 
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="https://t3.ftcdn.net/jpg/05/16/27/58/240_F_516275801_f3Fsp17x6HQK0xQgDQEELoTuERO4SsWV.jpg">
    </div>    
    <div class="message">{{MSG}}</div>
</div>
'''
