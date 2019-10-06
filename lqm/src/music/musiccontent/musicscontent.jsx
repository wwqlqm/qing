import  React from 'react'

class MusicContent extends React.Component{
    constructor(pros){
        super(pros)

    }
    render() {
        return (
            <div>
                <audio controls src='http://103.78.124.74:83/2Q2W2BBC3854D945269A1A82D5BCA597462DBFD9CA2B_unknown_46F22DA24436ECF9DE61D914B56FFDB7A58C2A9B_2/up_mp4.t57.cn/2018/1/03m/13/396131232171.m4a'>
                </audio>
                <video src="http://103.78.124.72:83/2Q2WFF9BFD18A0190FA7C28E4D11DC3797C5DD4FD8A8_tbvideomp4_2E08317623F0ACCAE79D12B75C671ABD24DA9BBB_12/vd2.bdstatic.com/mda-jik4xgz3yzt3p6m1/mda-jik4xgz3yzt3p6m1.mp4" controls="controls">
                </video>
            </div>
        )
    }
}
export  default MusicContent
