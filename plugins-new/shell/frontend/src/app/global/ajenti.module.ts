import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { AjentiHammerJSProvider } from '@ajenti/core/AjentiHammerJSProvider';
import { BrowserModule, HammerModule } from '@angular/platform-browser';
import { ProgressSpinnerComponent } from '@ajenti/components/progress-spinner/progress-spinner.component';
import { SmartProgressComponent } from '@ajenti/components/smart-progress/smart-progress.component';
import { FormatSecondsToDurationPipe } from '@ajenti/pipes/format-seconds-to-duration.pipe';
import { FormatBytesPipe } from '@ajenti/pipes/format-bytes.pipe';
import { AutoFocusDirective } from '@ajenti/directives/auto-focus.directive';
import { FormsModule, NgModel } from '@angular/forms';
import { GlobalConstants, TranslateModule, TranslateModuleConfig, TranslateService } from '@ngx-ajenti/core';
import { AjentiTranslateLoader } from '@ajenti/core/AjentiTranslateLoader';
import { ToastrModule } from 'ngx-toastr';

const initialConfigContent = ((window as any).globalConstants as GlobalConstants)?.initialConfigContent;
const translateModuleConfig: TranslateModuleConfig = {
  defaultLanguage: initialConfigContent?.language || 'en',
  loader: AjentiTranslateLoader,
};

@NgModule({
  declarations: [
    ProgressSpinnerComponent,
    SmartProgressComponent,
    FormatSecondsToDurationPipe,
    FormatBytesPipe,
    AutoFocusDirective,
  ],
  imports: [
    BrowserModule,
    CommonModule,
    HammerModule,
    NgbModule,
    FormsModule,
    ToastrModule.forRoot(),
    TranslateModule.forRoot(translateModuleConfig),
  ],
  providers: [
    AjentiHammerJSProvider,
    TranslateService,
  ],
  exports: [
    BrowserModule,
    HammerModule,
    NgbModule,
    CommonModule,
    FormsModule,
    TranslateModule,
    ProgressSpinnerComponent,
    SmartProgressComponent,
    FormatSecondsToDurationPipe,
    FormatBytesPipe,
    AutoFocusDirective,
    NgModel,
    ToastrModule,
  ],
})
export class AjentiModule {
}
