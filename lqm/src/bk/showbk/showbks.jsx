import React from 'react'
import {Row,Col,Card,List,Avatar,Input,Tag} from 'antd'
const {Meta} = Card;
const {Search} = Input
class SHOWBK extends  React.Component{
    constructor(pros){
        super(pros)
        this.state={
            data : [
                {
                    title: 'Ant Design Title 1',
                },
                {
                    title: 'Ant Design Title 2',
                },
                {
                    title: 'Ant Design Title 3',
                },
                {
                    title: 'Ant Design Title 4',
                },
            ],
        }
    }

    render() {
        return (
            <div>
               <Row>
                   <Col span={6}>
                       <Row>
                           <Card
                               hoverable
                               // style={{ width: 240 }}
                               cover={<img alt="example" src="https://os.alipayobjects.com/rmsportal/QBnOOoLaAfKPirc.png" />}
                           >
                               <Meta title="Europe Street beat" description="www.instagram.com" />
                           </Card>,
                       </Row>
                       <Row>
                           <Card size="small" title="时间分类" extra={<a href="#">More</a>}>
                               <p>Card content</p>
                               <p>Card content</p>
                               <p>Card content</p>
                           </Card>
                       </Row>
                       <br/>
                       <Row>
                           <div>
                               <Search placeholder="input search text" onSearch={value => console.log(value)} enterButton />

                           </div>
                       </Row>
                       <br/>
                       <Row>
                           <Card size="small" title="标签" extra={<a href="#">More</a>}>
                               <Tag color="magenta">magenta</Tag>
                               <Tag color="red">red</Tag>
                               <Tag color="volcano">volcano</Tag>
                               <Tag color="orange">orange</Tag>
                               <Tag color="gold">gold</Tag>
                               <Tag color="lime">lime</Tag>
                               <Tag color="green">green</Tag>
                               <Tag color="cyan">cyan</Tag>
                               <Tag color="blue">blue</Tag>
                               <Tag color="geekblue">geekblue</Tag>
                               <Tag color="purple">purple</Tag>
                           </Card>
                       </Row>
                   </Col>
                   <Col span={12} offset={2}>
                       <List
                           itemLayout="horizontal"
                           dataSource={this.state.data}
                           renderItem={item => (
                               <List.Item style={{marginTop:'10px',textAlign:'left'}} >
                                   <List.Item.Meta
                                       avatar={<Avatar src="https://zos.alipayobjects.com/rmsportal/ODTLcjxAfvqbxHnVXCYX.png" />}
                                       title={<a href="https://ant.design">{item.title}</a>}
                                       description="Ant Design, a design language for background applications, is refined by Ant UED Team"
                                   />
                               </List.Item>
                           )}
                       />
                   </Col>
               </Row>
            </div>
        )
    }
}

export  default SHOWBK
