import  React from 'react'
import {Row,Col,Affix} from 'antd'
class MusicContent extends React.Component{
    constructor(pros) {
        super(pros)
        this.state = {
            top: 10,
            bottom: 10,
        };
    }


    render() {
        return (
            <div>
                {/*<audio style={{width:'500px'}} controls src='http://103.78.124.74:83/2Q2W2BBC3854D945269A1A82D5BCA597462DBFD9CA2B_unknown_46F22DA24436ECF9DE61D914B56FFDB7A58C2A9B_2/up_mp4.t57.cn/2018/1/03m/13/396131232171.m4a'>*/}
                {/*</audio>*/}
                <div className="fixed" style={{position:'fixed',bottom:'10px'}}>
                    <Row style={{height:'100px',lineAlign:'left'}}>
                        <Col span={4} offset={4} >
                            <div>
                                <img style={{height:'100px'}} src="https://os.alipayobjects.com/rmsportal/QBnOOoLaAfKPirc.png" alt=""/>
                            </div>
                        </Col>
                        {/*<Col span={4} offset={4} >*/}
                        {/*    <div>*/}
                        {/*        <img style={{height:'100px'}} src="https://os.alipayobjects.com/rmsportal/QBnOOoLaAfKPirc.png" alt=""/>*/}
                        {/*    </div>*/}
                        {/*</Col>*/}
                        <Col span={10} offset={4}>
                            <Row span={24}>
                                <div style={{lineAlign:'left'}}>标题是啥</div>
                            </Row>
                            <Row span={24}>
                                <div className={'btn-audio'}>
                                    <audio className={'audio'} style={{width:'500px'}}  src='http://103.78.124.74:83/2Q2W2BBC3854D945269A1A82D5BCA597462DBFD9CA2B_unknown_46F22DA24436ECF9DE61D914B56FFDB7A58C2A9B_2/up_mp4.t57.cn/2018/1/03m/13/396131232171.m4a'>
                                    </audio>
                                </div>
                            </Row>
                        </Col>
                    </Row>
                </div>

            </div>
        )
    }
}
export  default MusicContent
