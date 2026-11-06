/**
 * 咪噜 · 铜仁 AI 管家
 * 对话接口：POST /api/v1/ai/chat（DeepSeek / 小米 MiMo，后端自动降级）
 */
const api = require('../../common/api');

const app = getApp();

// 兜底预设提示词（接口未返回时使用）
const FALLBACK_PRESETS = [
  { icon: 'sun', text: '铜仁今天天气适合玩什么项目？' },
  { icon: 'mountain', text: '梵净山今天人多不多？' },
  { icon: 'route', text: '梵净山哪条路好爬一些？' },
  { icon: 'food', text: '铜仁必吃的三个小吃是什么？' },
  { icon: 'pin', text: '第一次来铜仁，两天怎么安排？' },
  { icon: 'star', text: '带老人小孩去铜仁，推荐哪些景点？' }
];

Page({
  data: {
    statusBar: app.globalData.statusBarHeight,
    icons: {
      back: api.toIconUrl('arrow-left', 'ink')
    },
    messages: [],
    presets: FALLBACK_PRESETS,
    quickShow: true,
    inputValue: '',
    sending: false,
    scrollTarget: '',
    providerLabel: 'DeepSeek · 已就绪'
  },

  onLoad() {
    this._seq = 0;
    this.pushMessage(
      'assistant',
      '哈喽～我是咪噜，你的铜仁 AI 小管家！天气、景点人多不多、路线好不好爬、吃什么，咪噜都能帮你参谋～',
      { provider: '咪噜' }
    );
    this.loadPresets();
  },

  loadPresets() {
    api.getMiluPrompts()
      .then((res) => {
        const list = (res && res.list) || [];
        if (list.length) this.setData({ presets: list });
      })
      .catch(() => {});
  },

  nextId() {
    this._seq += 1;
    return 'msg-' + this._seq;
  },

  pushMessage(role, content, extra) {
    const id = this.nextId();
    const msg = Object.assign(
      { id: id, role: role, content: content, time: this._now() },
      extra || {}
    );
    const messages = this.data.messages.concat(msg);
    this.setData({ messages: messages, scrollTarget: id });
    return msg;
  },

  updateMessage(id, patch) {
    const messages = this.data.messages.map((m) =>
      m.id === id ? Object.assign({}, m, patch) : m
    );
    this.setData({ messages: messages, scrollTarget: id });
  },

  _now() {
    const d = new Date();
    const pad = (n) => (n < 10 ? '0' + n : '' + n);
    return pad(d.getHours()) + ':' + pad(d.getMinutes());
  },

  onInput(e) {
    this.setData({ inputValue: e.detail.value });
  },

  onPromptTap(e) {
    const text = e.currentTarget.dataset.text;
    if (this.data.sending) return;
    this.send(text);
  },

  onSendTap() {
    this.send(this.data.inputValue);
  },

  send(rawText) {
    const text = (rawText || '').trim();
    if (!text || this.data.sending) return;

    this.setData({ quickShow: false, inputValue: '' });
    this.pushMessage('user', text);

    // 历史对话（排除刚加入的用户消息与欢迎语）
    const history = this.data.messages
      .filter((m) => m.role === 'user' || m.role === 'assistant')
      .slice(0, -1)
      .filter((m) => !m.welcome)
      .map((m) => ({ role: m.role, content: m.content }))
      .slice(-8);

    this.setData({ sending: true });
    this._pendingId = this.nextId();
    const pending = {
      id: this._pendingId,
      role: 'assistant',
      content: '',
      pending: true,
      time: this._now()
    };
    this.setData({
      messages: this.data.messages.concat(pending),
      scrollTarget: this._pendingId
    });

    api.chatWithMilu({ message: text, history: history })
      .then((res) => {
        const reply = (res && res.reply) || '咪噜刚刚走神啦，可以再说一次吗？';
        const provider = (res && res.provider) || '';
        const model = (res && res.model) || '';
        this.setData({ sending: false });
        this.updateMessage(this._pendingId, {
          content: reply,
          pending: false,
          provider: provider ? provider + (model && model !== 'offline' ? ' · ' + model : '') : ''
        });
        if (provider) {
          this.setData({ providerLabel: provider + ' · 在线' });
        }
      })
      .catch((err) => {
        this.setData({ sending: false });
        this.updateMessage(this._pendingId, {
          content: '咪噜这边网络有点卡，要不稍后再问一次？也可以先看看首页的景点推荐哦～',
          pending: false,
          error: true
        });
        app.toast(err.message || '咪噜暂时无法回答');
      });
  },

  onBack() {
    wx.navigateBack();
  }
});
