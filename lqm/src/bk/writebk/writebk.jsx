import React from 'react'
import {Row,Input} from 'antd'
import Editor from 'for-editor'
const {Search} = Input
class writebk extends React.Component{
    constructor(props){
        super(props)
        this.state={
            makedown :'',
            html:'',
            value:'',
        }
    }
    handleChange(value){
        this.setState({
            value
        })
    }


    render() {
        return (
            <div style={{padding:'10px 0'}}>
                <div style={{display:'flex'}}>
                    {/*<Input/>*/}
                    {/*<Button>提交</Button>*/}
                    <Search
                        placeholder="标题"
                        enterButton="提交"
                        size="large"
                        onSearch={value => console.log(value)}
                    />
                </div>
               <Row style={{padding:'10px 0',textAlign:'left'}}>
                   <Editor value={this.state.value}  onChange={this.handleChange.bind(this)}></Editor>
               </Row>
            </div>
        )

}}
export  default  writebk
