import { templatePostApi, templateGetApi, templateDeleteApi, templatePutApi} from './api';
import {
  ProSkeleton,
} from '@ant-design/pro-components';
import { Button, message } from 'antd';
import React, { useRef, useState ,useCallback, useEffect} from 'react';
import { useModel } from '@umijs/max';
import TemplateComponentPrivate from './components/TemplateComponentPrivate';
import TemplateComponentCommon from '@/components/TemplateComponentCommon';
// import styles from './index.less';
import  './index.less';
import img from '@/utils/img'
import * as THREE from 'three';
import { TrackballControls } from 'three/examples/jsm/controls/TrackballControls';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { RGBELoader } from 'three/examples/jsm/loaders/RGBELoader';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';

const lrcText=`[00:00.00] 作词 : 陈一豪Clear
[00:00.98] 作曲 : 陈一豪Clear
[00:01.96] 编曲 : Newyounggo
[00:02.94] 混音 : AaronGwin
[00:03.92] 母带 : AaronGwin
[00:04.90] 封面拍摄 : 罗宗汉 Ro
[00:05.88] 统筹 : 胡艺伟/KK
[00:06.86] 出品人 : 车澈/肇卜羲@INDE COMPANY
[00:07.84] 出品 : INDE COMPANY/网易音乐人
[00:08.82] 制作人 : 陈一豪Clear
[00:09.81]你怎么回忆我？
[00:11.40]在你决定了失联的那刻
[00:13.98]我想我的心就死了
[00:16.29]该断了念想
[00:17.55]好想变健忘
[00:18.78]可总发了疯的迷恋
[00:21.12]我迷恋有期待的感觉
[00:23.61]可这些都被堵了
[00:25.89]伴着我伤感
[00:27.18]特别在夜晚
[00:28.38]像鼻塞
[00:32.73] I’ m outside
[00:33.69]（游荡在街上）
[00:35.10] I’ m not sad
[00:35.88]（我怎么会伤心呢）
[00:37.41]麻木算罪过
[00:38.91]你把热烈还给我
[00:41.43] Roll the dice
[00:42.33]（感情像骰子被随意抛掷）
[00:45.06] I’ m not mind
[00:46.41]（可我并不在乎）
[00:46.77]就这样褪色
[00:48.51]请恕我无法配合
[00:51.93] I’ m outside
[00:52.86]（游荡在街上）
[00:54.30] I’ m not sad
[00:55.08]（我怎么会伤心呢）
[00:56.64]麻木算罪过
[00:58.14]你把热烈还给我
[01:01.29] Roll the dice
[01:02.79]（感情像骰子被随意抛掷）
[01:04.29] I’ m not mind
[01:05.61]（可我并不在乎）
[01:05.97]就这样褪色
[01:07.71]请恕我无法配合
[01:10.38]复杂的情愫
[01:11.52]我没法再祝你幸福
[01:13.95]这个圣诞独自庆祝
[01:16.32]再也没有人值得我倾诉
[01:18.81]靠在我肩上
[01:20.01]认真地看我
[01:21.15]“决定了吻我前你最好想清楚”
[01:25.08]爱我你也说过
[01:27.00]现在是你退缩了
[01:29.46]你的耳环是我的书签
[01:31.98]软软的吻拨动我的湖面
[01:34.29]没法再融入聚会聊天
[01:36.69]喧闹像伤心的和弦
[01:39.09]我的浪漫都死在这天
[01:41.82]不再热烈才算搁浅
[01:44.73]像鼻塞缠着我
[01:46.77]难呼吸才可怜
[01:53.79]麻木算罪过
[01:55.59]你把热烈还给我
[02:03.42]就这样褪色
[02:05.28]请恕我无法配合
[02:11.13] I’ m outside
[02:12.09]（游荡在街上）
[02:13.47] I’ m not sad
[02:14.28]（我怎么会伤心呢）
[02:15.84]麻木算罪过
[02:17.28]你把热烈还给我
[02:19.83] Roll the dice
[02:20.73]（感情像骰子被随意抛掷）
[02:23.46] I’ m not mind
[02:24.81]（可我并不在乎）
[02:25.17]就这样褪色
[02:26.88]请恕我无法配合
[02:30.33] I’ m outside
[02:31.26]（游荡在街上）
[02:32.67] I’ m not sad
[02:34.47]（我怎么会伤心呢）
[02:35.01]麻木算罪过
[02:36.51]你把热烈还给我
[02:39.00] Roll the dice
[02:39.99]（感情像骰子被随意抛掷）
[02:42.69] I’ m not mind
[02:44.01]（可我并不在乎）
[02:44.37]就这样褪色
[02:46.08]请恕我无法配合`

export default () => {
  const {
    serviceParamsGet,
    setServiceParamsGet,
    serviceParamsPost,
    setServiceParamsPost,
    serviceParamsPut,
    setServiceParamsPut,
    serviceParamsDelete,
    setServiceParamsDelete,
    componentParamsPrivate,
    setComponentParamsPrivate
  } = useModel('Template.model');
  const lyricsParent=useRef<any>();
  const currentTime=useRef<any>(0);
  const lyricsHtmlRefs = useRef<any>([]);
  const [lyricsHtml,setLyricsHtml]=useState<any>([])
  const [lyricsTimeAndText,setLyricTimeAndText]=useState<any>([])
  // 解析歌词
  const parseLyric=(lrcText)=>{
      const lines = lrcText.split('\n');
      const lyrics:any[] = [];
      
      lines.forEach(line => {
          // 匹配 [mm:ss.xx] 格式的时间戳
          const match = line.match(/^\[(\d{2}):(\d{2}\.\d{2,3})\](.*)/);
          if (match) {
              const minutes = parseFloat(match[1]);
              const seconds = parseFloat(match[2]);
              const time = minutes * 60 + seconds;
              const text = match[3].trim();
              
              lyrics.push({ time, text });
          }
      });
      
      return lyrics;
  }

  // 根据当前时间找到对应歌词行
  const findCurrentLyricIndex=useCallback((currentTime)=>{
      for (let i = lyricsTimeAndText.length - 1; i >= 0; i--) {
          if (currentTime >= lyricsTimeAndText[i].time) {
              return i;
          }
      }
      return -1;
  },[lyricsTimeAndText])

  // 滚动歌词到当前播放位置
  const scrollLyric=useCallback((index)=>{
      if (lyricsHtmlRefs.current[index]) {
          // 移除之前的高亮
          lyricsHtmlRefs.current.forEach(line => {
              line.classList.remove('active', 'past');
          });
          
          // 设置之前歌词的样式
          for (let i = 0; i < index; i++) {
              lyricsHtmlRefs.current[i].classList.add('past');
          }
          
          // 高亮当前歌词
          lyricsHtmlRefs.current[index].classList.add('active');
          
          // 计算滚动位置
          const containerHeight = lyricsParent.current.parentElement.clientHeight;
          const lineHeight = lyricsHtmlRefs.current[index].offsetHeight;
          const scrollTop = lyricsHtmlRefs.current[index].offsetTop - containerHeight / 2 + lineHeight / 2;
          
          // 应用滚动动画
          lyricsParent.current.style.transform = `translateY(-${scrollTop}px)`;
      }
  },[])

  // 初始化歌词显示
  const initLyrics=useCallback(()=>{
      const newLyricsTimeAndText:any[] = parseLyric(lrcText);
      setLyricTimeAndText(newLyricsTimeAndText)
      
      // 生成歌词DOM
      let newLyricsHtml=[] as any;
      newLyricsTimeAndText.forEach((lyric,index) => {
          newLyricsHtml.push(<div className = 'lyric-line'  ref={el => lyricsHtmlRefs.current[index] = el} key={index} >
            {lyric.text || '♪'}
          </div>)
      });
      setLyricsHtml(newLyricsHtml)
  },[])

  useEffect(() => {
    initLyrics()
  }, [initLyrics]);

  useEffect(() => {
    let playbackInterval
    if(lyricsHtml.length>0&&lyricsTimeAndText.length>0){
      playbackInterval = setInterval(() => {
          currentTime.current += 0.1;
          if (currentTime.current >= lyricsTimeAndText[lyricsTimeAndText.length-1].time) {
              currentTime.current = 0;
          }
          const lyricIndex = findCurrentLyricIndex(currentTime.current);
          if (lyricIndex >= 0) {
              scrollLyric(lyricIndex);
          }
      }, 100);
    }
    return ()=>{
      if(playbackInterval){
        clearInterval(playbackInterval)
      }
    }

  }, [findCurrentLyricIndex, lyricsHtml.length, lyricsTimeAndText, scrollLyric]);

  return (
    <div className="global">
        <div className="lyrics-container" >
            <div className="lyrics-mask"></div>
            <div className="lyrics-parent" ref={lyricsParent}>
              {lyricsHtml}
            </div>
        </div>
    </div>
  );
};
