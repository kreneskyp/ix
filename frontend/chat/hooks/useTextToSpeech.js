import { useEffect, useState } from "react";

const useTextToSpeech = () => {
  const [speech, setSpeech] = useState(null);
  const [paused, setPaused] = useState(true);

  useEffect(() => {
    const synth = window.speechSynthesis;

    const speak = (text) => {
      const utterance = new SpeechSynthesisUtterance(text);
      synth.speak(utterance);
    };

    const handlePausedChange = () => {
      setPaused(synth.paused);
      if (!synth.paused) {
        setSpeech({ speak });
      }
    };

    synth.addEventListener("pause", handlePausedChange);
    synth.addEventListener("resume", handlePausedChange);

    return () => {
      synth.removeEventListener("pause", handlePausedChange);
      synth.removeEventListener("resume", handlePausedChange);
    };
  }, []);

  const onPaused = (handler) => {
    if (paused) {
      handler();
    }
  };

  return { speech, onPaused };
};

export default useTextToSpeech;
