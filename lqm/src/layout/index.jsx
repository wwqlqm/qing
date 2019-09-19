import React,{Component} from 'react';
import 'antd/dist/antd.css';
import {BrowserRouter,Redirect,Route} from 'react-router-dom'
import Login from '../../src/login/login'
import  {Switch} from 'react-router-dom'
import Else from '../../src/layout/layout'
class  LL extends Component{
    render(){
        return (

            <BrowserRouter>
                <Switch>
                    <Route path='/login' component={Login}/>
                    <Route path='/else' component={Else}/>
                    <Redirect from='/' to='/login'></Redirect>
                </Switch>
            </BrowserRouter>
        );
    }

}

export default LL;
