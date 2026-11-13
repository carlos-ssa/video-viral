import * as Tone from 'tone';

// All randomness is explicit; Web Audio oscillator rendering may differ across browsers.
window.renderSound = async spec => {
  let state = spec.seed >>> 0;
  const random = () => { state = (Math.imul(state, 1664525) + 1013904223) >>> 0; return state / 4294967296; };
  const rendered = await Tone.Offline(() => {
    for (const e of spec.events) {
      const gain = new Tone.Gain(0).toDestination();
      const level = Math.pow(10, e.gainDb / 20) * 0.28;
      const end = e.at + e.duration;
      const attack = Math.min(0.025, e.duration * 0.2);
      gain.gain.setValueAtTime(0, e.at);
      gain.gain.linearRampToValueAtTime(level, e.at + attack);
      gain.gain.linearRampToValueAtTime(0, end);
      const jitter = 0.94 + random() * 0.12;
      const settings = {
        whoosh: [550, 110, 'sawtooth'], impact: [125, 42, 'sine'],
        pop: [650, 220, 'sine'], riser: [180, 1400, 'sawtooth'], pulse: [240, 240, 'square']
      }[e.type];
      const osc = new Tone.Oscillator(settings[0] * jitter, settings[2]).connect(gain);
      osc.frequency.setValueAtTime(settings[0] * jitter, e.at);
      osc.frequency.exponentialRampToValueAtTime(settings[1] * jitter, end);
      osc.start(e.at).stop(end);
    }
  }, spec.duration, 1, 44100);
  return rendered.getChannelData(0);
};
