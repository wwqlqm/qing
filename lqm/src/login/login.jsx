import React,{Component} from "react";
import {Input,Form,Button,Icon,Checkbox} from "antd";



class NormalLoginForm extends React.Component {

    handleSubmit = e => {
        e.preventDefault();
        this.props.form.validateFields((err, values) => {
            if (!err) {
                console.log('Received values of form: ', values);
            }
        });
    };

    render() {
        const { getFieldDecorator } = this.props.form;
        return (
            <Form onSubmit={this.handleSubmit} className="login-form" style={{width:'300px'}}>
                <Form.Item>
                    {getFieldDecorator('username', {
                        rules: [{ required: true, message: 'Please input your username!' }],
                    })(
                        <Input
                            prefix={<Icon type="user" style={{ color: 'rgba(0,0,0,.25)' }} />}
                            placeholder="Username"
                        />,
                    )}
                </Form.Item>
                <Form.Item>
                    {getFieldDecorator('password', {
                        rules: [{ required: true, message: 'Please input your Password!' }],
                    })(
                        <Input
                            prefix={<Icon type="lock" style={{ color: 'rgba(0,0,0,.25)' }} />}
                            type="password"
                            placeholder="Password"
                        />,
                    )}
                </Form.Item>
                <Form.Item>
                    {getFieldDecorator('remember', {
                        valuePropName: 'checked',
                        initialValue: true,
                    })(<Checkbox>Remember me</Checkbox>)}
                    <a className="login-form-forgot" href="">
                        Forgot password
                    </a>
                    <div>
                        <Button type="primary" htmlType="submit" className="login-form-button" style={{width:'100%'}} >
                            Log in
                        </Button>
                    </div>

                    Or <a href="">register now!</a>
                </Form.Item>
            </Form>
        );
    }
}
const WrappedNormalLoginForm = Form.create({ name: 'normal_login' })(NormalLoginForm);


class Login extends Component{

    constructor (props) {
        super(props);
        this.state={
            num:1
        }
    }


    render(){
        return (
            <div style={{background:`url(${require('./login.jpg')}) no-repeat center center`,backgroundSize:'100%',height:'650px',}}>
                <div style={{background:'white',width:"400px",display:'flex',justifyContent:'center',alignItems:'center',position:'absolute',right:'30px',bottom:'260px',paddingTop:'40px',borderRadius:'20px'}} >
                    <WrappedNormalLoginForm ></WrappedNormalLoginForm>
                </div>
            </div>
        )
    }
}




export  default  Login
