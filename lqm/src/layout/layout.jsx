import { Layout, Menu, Breadcrumb } from 'antd';
import  React from 'react'
import './laout.css'
import BK from '../bk'
import BOOK from '../book'
import MUSIC from '../music'
import MOVIES from '../movies'

import {Switch,Route} from 'react-router-dom'
const { Header, Content, Footer } = Layout;

class Layouts extends React.Component{
    constructor (props) {
        super(props);
    }
    render() {
        return (
            <div>
                <Layout className="layout">
                    <Header>
                        <div className="logo" />
                        <Menu
                            theme="dark"
                            mode="horizontal"
                            defaultSelectedKeys={['1']}
                            style={{ lineHeight: '64px' }}
                            onClick={(item)=>{
                                if(item.key==1){
                                    this.props.history.push('/else/bk')

                                }
                                if(item.key==2){
                                    this.props.history.push('/else/book')
                                }
                                if(item.key==3){
                                    this.props.history.push('/else/music')
                                }
                                if(item.key==4){
                                    this.props.history.push('/else/movies')
                                }
                            }}
                        >
                            <Menu.Item key="1">博客</Menu.Item>
                            <Menu.Item key="2">书籍</Menu.Item>
                            <Menu.Item key="3">音乐</Menu.Item>
                            <Menu.Item key="4">电影</Menu.Item>
                        </Menu>
                    </Header>
                    <Content style={{ padding: '0 50px' }}>
                        <Switch>
                            <Route path={this.props.match.path+'/bk'} component={BK} ></Route>
                            <Route path={this.props.match.path+'/book'} component={BOOK} ></Route>
                            <Route path={this.props.match.path+'/music'} component={MUSIC} ></Route>
                            <Route path={this.props.match.path+'/movies'} component={MOVIES} ></Route>
                        </Switch>
                    </Content>
                    <Footer style={{ textAlign: 'center' }}></Footer>
                </Layout>
            </div>
        )

}}

export  default  Layouts
