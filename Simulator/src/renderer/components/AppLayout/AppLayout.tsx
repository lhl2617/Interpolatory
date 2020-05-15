/* eslint-disable */
import * as React from 'react';
import { Layout, Menu, Button } from 'antd';
import Benchmark from '../Pages/Benchmark/Benchmark';
import Convert from '../Pages/Convert/Convert';
import Test from '../Pages/Test/Test';
import Info from '../Pages/Info/Info';
import Home from '../Pages/Home/Home';
import { minApp, closeApp, maxApp } from '../../util';

const { SubMenu } = Menu;
const { Header, Content, Sider } = Layout;

const logo = require('../../../../assets/img/headerlogo.png').default;

const homeIcon = require('../../../../assets/img/home.png').default;
const convertIcon = require('../../../../assets/img/convert.png').default;
const benchmarkIcon = require('../../../../assets/img/benchmark.png').default;
const testIcon = require('../../../../assets/img/test.png').default;
const infoIcon = require('../../../../assets/img/info.png').default;


const minIcon = require('../../../../assets/img/window/min.png').default;
const maxIcon = require('../../../../assets/img/window/max.png').default;
const closeIcon = require('../../../../assets/img/window/close.png').default;


type CurrentPage = 'home' | 'convert' | 'benchmark' | 'test' | 'info';

type IState = {
    currentPage: CurrentPage;
    height: number;
};

export class AppLayout extends React.Component<{}, IState> {
    constructor(props: any) {
        super(props);
        this.state = {
            currentPage: 'home',
            height: 768,
        };
    }

    componentDidMount = () => {
        /*
            TODO:-
                1. Check python3 exists
                2. Check localStorage for dependency installation
                3. Check main.py exists
        */

        this.updateWindowDimensions();
        window.addEventListener('resize', this.updateWindowDimensions);
    }

    componentWillUnmount = () => {
        window.removeEventListener('resize', this.updateWindowDimensions);
    }

    updateWindowDimensions = () => {
        this.setState({ height: window.innerHeight });
    }


    getContent = (currentPage: CurrentPage) => {
        if (currentPage === "home") return <Home />;
        if (currentPage === "benchmark") return <Benchmark />;
        if (currentPage === "convert") return <Convert />;
        if (currentPage === "test") return <Test />;
        if (currentPage === "info") return <Info />;
        console.error('Invalid currentPage');
    }

    gotoPage = (page: CurrentPage) => {
        this.setState({
            currentPage: page
        })
    }

    render() {
        const { currentPage, height } = this.state;
        return (
            <Layout>
                <Header className="header">
                    <img
                        id='header-logo'
                        src={logo}
                        alt='Interpolatory Simulator'
                    />
                    <div style={{ float: 'right', color: 'white' }}>
                        <img className="window-btn" onClick={minApp} src={minIcon} alt="Min" />
                        <img className="window-btn" onClick={maxApp} src={maxIcon} alt="Max" />
                        <img className="window-btn" onClick={closeApp} src={closeIcon} alt="Close" />
                    </div>

                </Header>
                <Layout className="app-content">
                    <Sider width={200} className="site-layout-background sider">
                        <Menu
                            mode="inline"
                            defaultSelectedKeys={['0']}
                            theme="dark"
                            style={{ height: '100%', borderRight: 0 }}>
                            <Menu.Item 
                                key="0" 
                                icon={<img className="menu-icon" src={homeIcon} alt='Home' />} 
                                onClick={() => this.gotoPage('home')}>
                                    Home
                            </Menu.Item>
                            <Menu.Item 
                                key="1" 
                                icon={<img className="menu-icon" src={convertIcon} alt='Convert' />} 
                                onClick={() => this.gotoPage('convert')}>
                                    Convert
                            </Menu.Item>
                            <Menu.Item 
                                key="2" 
                                icon={<img className="menu-icon" src={benchmarkIcon} alt='Benchmark' />} 
                                onClick={() => this.gotoPage('benchmark')}>
                                    Benchmark
                            </Menu.Item>
                            <Menu.Item 
                                key="3" 
                                icon={<img className="menu-icon" src={testIcon} alt='Test' />} 
                                onClick={() => this.gotoPage('test')}>
                                    Test
                            </Menu.Item>
                            <Menu.Item 
                                key="4" 
                                icon={<img className="menu-icon" src={infoIcon} alt='Info' />} 
                                onClick={() => this.gotoPage('info')}>
                                    About
                            </Menu.Item>
                        </Menu>
                    </Sider>
                    <Layout style={{ padding: 24, height: height - 50, minWidth: 500 }}>
                        <Content
                            className="site-layout-background content"
                            style={{
                                padding: 24,
                                margin: 0,
                            }}>
                            {this.getContent(currentPage)}
                        </Content>
                    </Layout>
                </Layout>
            </Layout>
        );
    }
}

export default AppLayout;
