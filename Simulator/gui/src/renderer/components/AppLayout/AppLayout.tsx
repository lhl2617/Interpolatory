/* eslint-disable */
import * as React from 'react';
import { Layout, Menu } from 'antd';
import Benchmark from '../Pages/Benchmark/Benchmark';
import Convert from '../Pages/Convert/Convert';
import Test from '../Pages/Test/Test';
import Info from '../Pages/Info/Info';
import Home from '../Pages/Home/Home';
import { minApp, closeApp, maxApp } from '../../util';
import Estimate from '../Pages/Estimate/Estimate';
;
const { Header, Content, Sider } = Layout;

const logo = require('../../../../assets/img/headerlogo.png').default;

const homeIcon = require('../../../../assets/img/home.png').default;
const convertIcon = require('../../../../assets/img/convert.png').default;
const benchmarkIcon = require('../../../../assets/img/benchmark.png').default;
const testIcon = require('../../../../assets/img/test.png').default;
const infoIcon = require('../../../../assets/img/info.png').default;
const estIcon = require('../../../../assets/img/estimate.png').default;


const minIcon = require('../../../../assets/img/window/min.png').default;
const maxIcon = require('../../../../assets/img/window/max.png').default;
const closeIcon = require('../../../../assets/img/window/close.png').default;


type CurrentPage = 'home' | 'convert' | 'benchmark' | 'test' | 'info' | 'estimate';

type IState = {
    currentPage: CurrentPage;
    height: number;
    featuresEnabled: boolean; // this is to disable menu bars dependent on interpolatory backend
};

export class AppLayout extends React.Component<{}, IState> {
    constructor(props: any) {
        super(props);
        this.state = {
            currentPage: 'home',
            height: 720,
            featuresEnabled: false,
        };
    }

    componentDidMount = () => {
        this.updateWindowDimensions();
        window.addEventListener('resize', this.updateWindowDimensions);
    }

    componentWillUnmount = async () =>  {
        window.removeEventListener('resize', this.updateWindowDimensions);
    }

    updateWindowDimensions = async () => {
        this.setState({ height: window.innerHeight });
    }

    getContent = (currentPage: CurrentPage) => {
        if (currentPage === "home") return <Home setFeaturesEnabled={this.setFeaturesEnabled} />;
        if (currentPage === "benchmark") return <Benchmark />;
        if (currentPage === "convert") return <Convert />;
        if (currentPage === "test") return <Test />;
        if (currentPage === "estimate") return <Estimate />;
        if (currentPage === "info") return <Info />;
        console.error('Invalid currentPage');
    }

    gotoPage = async (page: CurrentPage) => {
        this.setState({
            currentPage: page
        })
    }

    setFeaturesEnabled = async (b: boolean) => {
        const { featuresEnabled } = this.state;
        if (featuresEnabled !== b) {
            this.setState({ featuresEnabled: b });
        }
    };

    render() {
        const { currentPage, height, featuresEnabled } = this.state;
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
                                onClick={() => this.gotoPage('convert')}
                                disabled={!featuresEnabled}>
                                Convert
                            </Menu.Item>
                            <Menu.Item
                                key="2"
                                icon={<img className="menu-icon" src={benchmarkIcon} alt='Benchmark' />}
                                onClick={() => this.gotoPage('benchmark')}
                                disabled={!featuresEnabled}>
                                Benchmark
                            </Menu.Item>
                            <Menu.Item
                                key="3"
                                icon={<img className="menu-icon" src={testIcon} alt='Test' />}
                                onClick={() => this.gotoPage('test')}
                                disabled={!featuresEnabled}>
                                Test
                            </Menu.Item>
                            <Menu.Item
                                key="4"
                                icon={<img className="menu-icon" src={estIcon} alt='Estimate' />}
                                onClick={() => this.gotoPage('estimate')}
                                disabled={!featuresEnabled}>
                                Estimate
                            </Menu.Item>
                            <Menu.Item
                                key="5"
                                icon={<img className="menu-icon" src={infoIcon} alt='Info' />}
                                onClick={() => this.gotoPage('info')}>
                                About
                            </Menu.Item>
                        </Menu>
                    </Sider>
                    <Layout style={{ padding: '0 24px 24px 24px', height: height - 50 }}>
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
