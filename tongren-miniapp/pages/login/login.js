/**
 * 登录 / 注册
 * POST /api/v1/user/login       { phone, password } → { token, user }
 * POST /api/v1/user/register    { phone, password, nickname } → { token, user }
 * 登录态写入 app.globalData 与 wx.storage（token / user），供收藏、行程、埋点接口鉴权
 */
const api = require('../../common/api');
const config = require('../../common/config');

const app = getApp();

const PHONE_RE = /^1\d{10}$/;

Page({
  data: {
    statusBar: app.globalData.statusBarHeight,

    icons: {
      back: api.toIconUrl('arrow-left', 'ink'),
      phone: api.toIconUrl('phone', 'green700'),
      shield: api.toIconUrl('shield', 'green700'),
      users: api.toIconUrl('users', 'green700'),
      seal: api.toIconUrl('seal', 'sandink')
    },

    mode: 'login',          // login | register
    phone: '',
    password: '',
    nickname: '',
    submitting: false,
    user: app.globalData.user || null,
    sealImgUrl: config.decoBase + 'deco-slogan-seal.png'
  },

  onShow() {
    // 从其他页面返回时同步登录态
    this.setData({ user: app.globalData.user || null });
    app.track('login_view', { page: 'pages/login/login' });
  },

  /* ---------------- 交互 ---------------- */

  onBack() {
    wx.navigateBack({
      fail: () => wx.switchTab({ url: '/pages/home/home' })
    });
  },

  onModeTap(e) {
    this.setData({ mode: e.currentTarget.dataset.mode });
  },

  onPhoneInput(e) {
    this.setData({ phone: e.detail.value });
  },

  onPasswordInput(e) {
    this.setData({ password: e.detail.value });
  },

  onNicknameInput(e) {
    this.setData({ nickname: e.detail.value });
  },

  onSubmit() {
    if (this.data.submitting) return;
    const phone = String(this.data.phone || '').trim();
    const password = String(this.data.password || '');
    const isRegister = this.data.mode === 'register';

    if (!PHONE_RE.test(phone)) {
      app.toast('请输入正确的 11 位手机号');
      return;
    }
    if (password.length < 6 || password.length > 32) {
      app.toast('密码长度需为 6–32 位');
      return;
    }

    this.setData({ submitting: true });
    const req = isRegister
      ? api.register(phone, password, String(this.data.nickname || '').trim())
      : api.login(phone, password);

    req
      .then((res) => {
        app.setLoginState(res.token, res.user);
        this.setData({ user: res.user, submitting: false, password: '' });
        app.track(isRegister ? 'register_success' : 'login_success', {
          page: 'pages/login/login'
        });
        wx.showToast({ title: isRegister ? '注册成功' : '登录成功', icon: 'success' });
      })
      .catch((err) => {
        this.setData({ submitting: false });
        app.toast((err && err.message) || '操作失败，请稍后重试');
      });
  },

  onLogout() {
    app.clearLoginState();
    this.setData({ user: null, mode: 'login', password: '' });
    app.toast('已退出登录');
  },

  onGoHome() {
    wx.switchTab({ url: '/pages/home/home' });
  }
});
