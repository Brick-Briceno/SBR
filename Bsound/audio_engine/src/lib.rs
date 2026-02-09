/*
* Audio Engine for SBR Aura and Bsound
* By @Brick_briceno 2026
*/

use std::sync::atomic::{AtomicBool, AtomicU32, AtomicUsize, AtomicF32, Ordering};
use std::sync::OnceLock;
use cpal::traits::{DeviceTrait, HostTrait, StreamTrait};

// Global state
struct AudioState {
    volume: AtomicF32,
    is_fading: AtomicBool,
    fade_step: AtomicF32,
    sample_rate: AtomicU32,
    current_sample: AtomicUsize,
}

static AUDIO_STATE: OnceLock<AudioState> = OnceLock::new();

fn get_audio_state() -> &'static AudioState {
    AUDIO_STATE.get_or_init(|| {
        let host = cpal::default_host();
        let device = host.default_output_device().expect("No output device");
        let config = device.default_output_config().unwrap();
        
        AudioState {
            volume: AtomicF32::new(1.0),
            is_fading: AtomicBool::new(false),
            fade_step: AtomicF32::new(0.0),
            sample_rate: AtomicU32::new(config.sample_rate().0),
            current_sample: AtomicUsize::new(0),
        }
    })
}

#[no_mangle]
pub extern "C" fn set_volume(level: f32) {
    let state = get_audio_state();
    state.volume.store(level.max(0.0).min(1.0), Ordering::Relaxed);
}

#[no_mangle]
pub extern "C" fn get_volume() -> f32 {
    get_audio_state().volume.load(Ordering::Relaxed)
}

#[no_mangle]
pub extern "C" fn start_fade_out(ms: f32) {
    if ms <= 0.0 {
        set_volume(0.0);
        return;
    }

    let state = get_audio_state();
    let sample_rate = state.sample_rate.load(Ordering::Relaxed) as f32;
    let total_samples = (ms / 1000.0) * sample_rate;
    
    state.fade_step.store(1.0 / total_samples, Ordering::Relaxed);
    state.is_fading.store(true, Ordering::Relaxed);
}

#[no_mangle]
pub extern "C" fn get_hardware_sample_rate() -> u32 {
    get_audio_state().sample_rate.load(Ordering::Relaxed)
}

struct AudioData {
    ptr_address: usize,
    len: usize,
}

#[no_mangle]
pub extern "C" fn play_audio_ptr(ptr: *const f32, len: usize, input_sample_rate: u32) -> i32 {
    let state = get_audio_state();
    let sample_rate = state.sample_rate.load(Ordering::Relaxed) as f64;
    let channels = 2; // Assuming stereo for simplicity
    
    let audio_data = AudioData {
        ptr_address: ptr as usize,
        len,
    };

    let playback_speed_factor = input_sample_rate as f64 / sample_rate;
    let mut current_frame_float: f64 = 0.0;

    let stream = match cpal::default_host()
        .default_output_device()
        .and_then(|device| {
            device.build_output_stream(
                &device.default_output_config()?.into(),
                move |data: &mut [f32], _| {
                    let audio_slice = unsafe {
                        std::slice::from_raw_parts(audio_data.ptr_address as *const f32, audio_data.len)
                    };

                    for frame in data.chunks_mut(channels) {
                        let frame_idx = current_frame_float as usize;
                        let next_frame = frame_idx + 1;
                        
                        if (frame_idx + 1) * channels > audio_slice.len() {
                            frame.fill(0.0);
                            continue;
                        }

                        let frac = (current_frame_float - frame_idx as f64) as f32;
                        
                        for c in 0..channels {
                            let idx = frame_idx * channels + c;
                            let next_idx = next_frame * channels + c;
                            
                            let s1 = if idx < audio_slice.len() { audio_slice[idx] } else { 0.0 };
                            let s2 = if next_idx < audio_slice.len() { audio_slice[next_idx] } else { 0.0 };
                            
                            let mut sample = s1 + (s2 - s1) * frac;
                            
                            // Apply volume and fade
                            let current_volume = state.volume.load(Ordering::Relaxed);
                            sample *= current_volume;
                            
                            if state.is_fading.load(Ordering::Relaxed) {
                                let new_volume = (current_volume - state.fade_step.load(Ordering::Relaxed)).max(0.0);
                                state.volume.store(new_volume, Ordering::Relaxed);
                                
                                if new_volume <= 0.0 {
                                    state.is_fading.store(false, Ordering::Relaxed);
                                }
                            }
                            
                            frame[c] = sample;
                        }
                        
                        current_frame_float += playback_speed_factor;
                        state.current_sample.store(current_frame_float as usize, Ordering::Relaxed);
                    }
                },
                |err| eprintln!("Audio stream error: {}", err),
                None
            )
        }) {
            Ok(stream) => stream,
            Err(e) => {
                eprintln!("Failed to create audio stream: {}", e);
                return 0;
            }
        };

    if let Err(e) = stream.play() {
        eprintln!("Failed to start playback: {}", e);
        return 0;
    }

    // Calculate and wait for playback to finish
    let duration_secs = len as f64 / (input_sample_rate as f64 * channels as f64);
    std::thread::sleep(std::time::Duration::from_secs_f64(duration_secs + 0.5));
    1
}

#[no_mangle]
pub extern "C" fn get_current_sample() -> usize {
    get_audio_state().current_sample.load(Ordering::Relaxed)
}
