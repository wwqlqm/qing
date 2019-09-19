import React,{Component} from 'react';

const  Login_data = React.createContext()

class Login_sever extends Component{
    constructor (props) {
        super(props);
        this.state={
            isLogin:true,
            user_info:[],
            login:this.login,
            loginout:this.loginout
        }
    }
    login(usernam,password){

    }
    loginout(){
        console.log(this.state.isLogin)
    }
    render() {
        return (<div>

        </div>)
    }

}


