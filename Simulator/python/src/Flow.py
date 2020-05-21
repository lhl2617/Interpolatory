from .Flows.liteflownet import liteflownet

FlowsDictionary = {
    'LiteFlowNet-Default': liteflownet.LiteFlowNetDefault,
    'LiteFlowNet-KITTI': liteflownet.LiteFlowNetKitti,
    'LiteFlowNet-SINTEL': liteflownet.LiteFlowNetSintel
}