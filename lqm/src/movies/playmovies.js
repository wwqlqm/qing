import  React from 'react'
import Player from 'griffith'

class MusicContent extends React.Component{
    constructor(pros){
        super(pros)

    }
    render() {
        const sources = {
            hd: {
                play_url: 'https://zhstatic.zhihu.com/cfe/griffith/zhihu2018_hd.mp4',
            },
            sd: {
                play_url: 'https://zhstatic.zhihu.com/cfe/griffith/zhihu2018_sd.mp4',
            },
        }
        return (
            <div style={{marginTop:'10px'}}>
                <Player sources={sources}/>
            </div>
        )
    }
}
export  default MusicContent
