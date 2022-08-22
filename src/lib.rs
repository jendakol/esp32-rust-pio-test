// #![no_std]
//
// use core::panic::PanicInfo;
//
// #[panic_handler]
// fn panic(info: &PanicInfo) -> ! {
//     // Your implementation goes here!
//     panic!()
// }

// #[no_mangle]
// #[export_name = "setup2"]
// extern "C" fn setup2() {
// }

#[no_mangle]
#[export_name = "hello_from_rust"]
extern "C" fn hello_from_rust() {
    println!("hi there!");
}

// #[no_mangle]
// #[export_name = "loop"]
// extern "C" fn arduino_loop() {
// }
